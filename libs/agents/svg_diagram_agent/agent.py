"""
Implementation of the SVG Diagram Agent, responsible for creating SVG diagram specifications and converting to PNG.
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional

from langchain.output_parsers import PydanticOutputParser
from langchain.tools import BaseTool

from libs.core.base_agent import BaseAgent
from libs.core.agent_response import AgentResponse
from libs.core.agent_status import AgentStatus
from libs.core.session import Session, Section, Slide
from libs.models.visualization_models import SVGDiagramSpec
import time
from .prompts import (
    svg_generation_prompt,
    svg_addition_prompt,
    svg_avoid_type_prompt
)
from .tools import create_svg_export_tool

logger = logging.getLogger(__name__)

class SVGDdiagramAgent(BaseAgent):
    """Agent responsible for creating SVG diagram specifications for slides."""
    
    agent_name = "svg_diagram_agent"
    description = "Creates SVG specifications for diagrams based on slide content and converts to PNG."
    
    def __init__(self, session: Session, **kwargs):
        """
        Initialize the SVG Diagram Agent.
        
        Args:
            session: The current session
            **kwargs: Additional keyword arguments
        """
        print("Initializing SVG Diagram Agent...")
        super().__init__(session, **kwargs)
        self.output_parser = PydanticOutputParser(pydantic_object=SVGDiagramSpec)
        
        self.general_prompt = svg_generation_prompt
        self.svg_addition_prompt = svg_addition_prompt
        self.svg_avoid_type_prompt = svg_avoid_type_prompt
        
        # Initialize tools
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """
        Initialize all SVG-related tools.
        """
        self.tools['svg_to_png'] = create_svg_export_tool()
        logger.info(f"Initialized {len(self.tools)} SVG tools")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
        
        Returns:
            The requested tool or None if not found
        """
        return self.tools.get(tool_name)
    
    def _get_prompt(self, section: Section, slide: Slide, additional_data: str = None, previously_used_diagram_types: List[str] | None = None) -> str:
        """
        Prepare the prompt for generating SVG diagram specifications.
        
        Args:
            section: The section data
            slide: The slide data
            additional_data: Additional data for prompt
            previously_used_diagram_types: List of diagram types to avoid
        
        Returns:
            The formatted prompt string
        """
        section_data = section.model_dump()
        del section_data['section_index']
        slide_data = slide.model_dump()
        del slide_data['section_index']
        del slide_data['slide_index']
        del slide_data['path']
        del slide_data['content']['layout_type']
        del slide_data['content']['layout']
        format_instructions = self.output_parser.get_format_instructions()
        
        self.session.output_message.add(f"Generating SVG diagram for slide #{slide.slide_index} of section #{section.section_index}", level="info")
        
        if previously_used_diagram_types:
            previously_used_diagram_types_str = ", ".join(previously_used_diagram_types)
            inputs = {
                "section": json.dumps(section_data, indent=2),
                "slide": json.dumps(slide_data, indent=2),
                "previously_used_diagram_types": previously_used_diagram_types_str,
            }
            formatted_prompt = self.svg_avoid_type_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt
        
        if additional_data:
            section_str = f"""
            Title: {section_data['title']}
            Description: {section_data['description']}
            Key Points: {section_data['key_points']}
            Estimated Slides: {section_data['estimated_slides']}
            Section Type: {section_data['section_type']}
            """
            slide_str = f"""
            Title: {slide_data['content']['title']}
            Content: {slide_data['content']['content']}
            Notes: {slide_data['content']['notes']}
            Keywords: {slide_data['content']['keywords']}
            Diagrams: {slide_data['diagrams']}
            """
            inputs = {
                "section": section_str,
                "slide": slide_str,
                "svg_code": slide.diagrams[0].content,
                "additional_data": additional_data,
            }
            formatted_prompt = self.svg_addition_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt
        
        inputs = {
            "section": json.dumps(section_data, indent=2),
            "slide": json.dumps(slide_data, indent=2),
        }
        formatted_prompt = self.general_prompt.partial(
            format_instructions=format_instructions
        ).format(**inputs)
        return formatted_prompt

    def run(self, 
            section_index: int,
            slide_index: int,
            diagram_path: str = None,
            additional_data: str = None,
            ) -> AgentResponse:
        """
        Generate SVG diagram specifications for a slide and convert to PNG.
        
        Args:
            section_index: Index of the section
            slide_index: Index of the slide within the section
            diagram_path: Path to save the PNG
            additional_data: Any additional data for diagram generation
        
        Returns:
            AgentResponse containing SVG specifications and PNG conversion results
        """
        slide = self.session.memory.get_slide_by_index(section_index=section_index, slide_index=slide_index)
        section = self.session.memory.get_session_by_index(index=section_index)
        diagram_path = diagram_path or slide.diagrams[0].path
        
        try:
            previously_drawn_diagrams = self.session.state.requirements.get("diagram_drawed", [])
            formatted_prompt = self._get_prompt(
                section=section,
                slide=slide,
                additional_data=additional_data,
                previously_used_diagram_types=previously_drawn_diagrams
            )
        
            self.session.save_prompt(key=section.section_index, type="svg_diagram", prompt=formatted_prompt)
            response = self.llm.invoke(formatted_prompt)
            svg_spec: SVGDiagramSpec = self.output_parser.invoke(response)
            self.session.memory.update_svg_code_by_index(
                section_index=section_index, slide_index=slide_index, svg_code=svg_spec.svg_code
            )
            
            logger.info(f"Successfully generated SVG diagram specification")
            
            response_data = svg_spec.model_dump()
            svg_tool = self.get_tool("svg_to_png")
            
            self.session.output_message.add(f"Converting SVG diagram to PNG and saving to {diagram_path}...", level="info")
            result = svg_tool._run(
                svg_code=svg_spec.svg_code,
                output_path=diagram_path
            )
            
            response_data["diagram_path"] = diagram_path
            
            if result.startswith("Error"):
                response_data["diagram_error"] = result
                all_diagram_types = ["flowchart", "hierarchy", "relationship", "timeline", "comparison"]
                current_type = svg_spec.diagram_type
                alternative_types = [t for t in all_diagram_types if t != current_type and t not in previously_drawn_diagrams]
                
                self.session.output_message.add(f"Initial SVG conversion failed. Will try {len(alternative_types)} alternative diagram types.", level="warning")
                
                alternative_success = False
                
                for alt_type in alternative_types:
                    try:
                        self.session.output_message.add(f"Trying with {alt_type} diagram...", level="info")
                        alternative_prompt = self._get_prompt(
                            section=section, 
                            slide=slide, 
                            additional_data=f"IMPORTANT: Fix invalid SVG syntax or create new diagram with type {alt_type}. Error: {result}.",
                            previously_used_diagram_types=previously_drawn_diagrams
                        )
                        
                        self.session.save_prompt(key=section.section_index, type="svg_diagram", prompt=alternative_prompt)
                        alternative_response = self.llm.invoke(alternative_prompt)
                        alternative_spec: SVGDiagramSpec = self.output_parser.invoke(alternative_response)
                        
                        alternative_result = svg_tool._run(
                            svg_code=alternative_spec.svg_code,
                            output_path=diagram_path
                        )
                        
                        if not alternative_result.startswith("Error"):
                            svg_spec = alternative_spec
                            response_data = svg_spec.model_dump()
                            response_data["diagram_path"] = diagram_path
                            self.session.output_message.add(f"Successfully generated alternative {svg_spec.diagram_type} SVG diagram.", level="info")
                            logger.info(f"Successfully generated alternative SVG diagram and saved to {diagram_path}")
                            alternative_success = True
                            
                            if alt_type not in previously_drawn_diagrams:
                                previously_drawn_diagrams.append(alt_type)
                            
                            break
                        else:
                            logger.info(f"Alternative diagram type {alt_type} also failed: {alternative_result}")
                    
                    except Exception as alt_error:
                        logger.error(f"Error with alternative diagram type {alt_type}: {str(alt_error)}")
                
                if not alternative_success:
                    error_message = f"Failed to generate SVG diagram with initial type '{current_type}' and all alternative types"
                    self.session.output_message.add(error_message, level="error")
                    response_data["diagram_error"] = error_message
            else:
                logger.info(f"Successfully generated SVG diagram and saved to {diagram_path}")
                if svg_spec.diagram_type not in previously_drawn_diagrams:
                    previously_drawn_diagrams.append(svg_spec.diagram_type)
            
            self.session.state.requirements["diagram_drawed"] = previously_drawn_diagrams
            
            self.session.add_draft(
                agent_name=self.agent_name,
                step="image_create_svg_diagram_specs",
                content={
                    "diagram_type": svg_spec.diagram_type,
                    "svg_spec": svg_spec.svg_code,
                    "diagram_path": response_data.get("diagram_path", ""),
                    "previously_drawn_diagrams": previously_drawn_diagrams
                },
            )
            
            self.session.save_drafts_to_json("drafts.json")
            
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully generated SVG diagram specification",
                data=response_data,
                metadata={}
            )
        
        except Exception as e:
            logger.error(f"Failed to generate SVG diagram specification: {str(e)}")
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to generate SVG diagram specification: {str(e)}",
                data={"raw_response": response if 'response' in locals() else "No response generated"}
            )