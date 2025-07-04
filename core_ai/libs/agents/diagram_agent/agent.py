"""
Implementation of the Diagram Agent, responsible for creating diagram specifications for slides.
"""

import logging
import os, json
from typing import List, Dict, Any, Optional

from langchain.output_parsers import PydanticOutputParser
from langchain.tools import BaseTool

from libs.core.base_agent import BaseAgent
from libs.core.agent_response import AgentResponse
from libs.core.agent_status import AgentStatus
from libs.core.session import Session, Section, Slide
from libs.models.visualization_models import DiagramSpec
import time
from .prompts import (
    diagram_generation_prompt,
    diagram_addition_prompt,
    diagram_advoid_type_prompt
)
from .tools import create_diagram_mermaid_tool

logger = logging.getLogger(__name__)


class DiagramAgent(BaseAgent):
    """Agent responsible for creating diagram specifications for slides."""
    
    agent_name = "diagram_agent"
    description = "Creates specifications for diagrams based on slide content."
    
    def __init__(self, session: Session, **kwargs):
        """
        Initialize the Diagram Agent.
        
        Args:
            session: The current session
            **kwargs: Additional keyword arguments
        """
        super().__init__(session, **kwargs)
        self.output_parser = PydanticOutputParser(pydantic_object=DiagramSpec)
        
        self.general_prompt = diagram_generation_prompt
        self.diagram_addition_prompt = diagram_addition_prompt
        self.diagram_advoid_type_prompt = diagram_advoid_type_prompt
        
        # Initialize tools
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """
        Initialize all diagram-related tools.
        """
        # Initialize Mermaid Tool
        self.tools['mermaid_to_png'] = create_diagram_mermaid_tool()
        
        # More tools can be added here in the future
        logger.info(f"Initialized {len(self.tools)} diagram tools")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
        
        Returns:
            The requested tool or None if not found
        """
        return self.tools.get(tool_name)
    
    def _get_prompt(self, section : Section, slide: Slide, additional_data: str = None, previously_used_diagram_types : List[str] | None = None) -> str:
        """
        Prepare the prompt for generating diagram specifications.
        
        Args:
            section: The section data
            slide: The slide data
        
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
        # Prepare the prompt with the section and slide data
        self.session.output_message.add(f"Generating diagram for section slide #{slide.slide_index} of section: #{section.section_index}", level="info")
        if previously_used_diagram_types:
            # Convert previously used diagram types to a string for the prompt
            previously_used_diagram_types_str = ", ".join(previously_used_diagram_types)
            inputs = {
                "section" : json.dumps(section_data, indent=2),
                "slide" : json.dumps(slide_data, indent=2),
                "previously_used_diagram_types": previously_used_diagram_types_str,
            }
            formatted_prompt = self.diagram_advoid_type_prompt.partial(
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
                "mermaid_code": slide.diagrams[0].content,
                "additional_data": additional_data,
            }
            formatted_prompt = self.diagram_addition_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt
        else:
            inputs = {
                "section" : json.dumps(section_data, indent=2),
                "slide" : json.dumps(slide_data, indent=2),
            }
            formatted_prompt = self.general_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt

            

    def run(self, 
            section_index: int,
            slide_index: int,
            diagram_path : str = None,
            additional_data: str = None,
            ) -> AgentResponse:
        """
        Generate diagram specifications for a slide and create the Mermaid diagram.
        
        Args:
            section_index: Index of the section
            slide_index: Index of the slide within the section
            additional_data: Any additional data for diagram generation
        
        Returns:
            AgentResponse containing diagram specifications and diagram generation results
        """
        slide = self.session.memory.get_slide_by_index(section_index=section_index, slide_index=slide_index)
        section = self.session.memory.get_session_by_index(index=section_index)
        diagram_path = diagram_path or slide.diagrams[0].path
        
        try:            
            # Get previously drawn diagram types from session state
            previously_drawn_diagrams = self.session.state.requirements.get("diagram_drawed", [])
            
            formatted_prompt = self._get_prompt(
                section=section,
                slide=slide,
                additional_data=additional_data
            )
        
            # Get response from LLM
            self.session.save_prompt(key=section.section_index, type="diagram", prompt=formatted_prompt)
            response = self.llm.invoke(formatted_prompt)
            diagram_spec : DiagramSpec = self.output_parser.invoke(response)
            self.session.memory.update_mermaid_code_by_index(
                section_index=section_index, slide_index=slide_index, mermaid_code=diagram_spec.mermaid_code
            )
            
            # Log success
            logger.info(f"Successfully generated diagram specification")
            
            # Response data and metadata for final return
            response_data = diagram_spec.model_dump()
            
            # Get the mermaid tool
            mermaid_tool = self.get_tool("mermaid_to_png")
            
            # Try to generate the diagram
            self.session.output_message.add(f"Generating Mermaid diagram and saving to {diagram_path}...", level="info")
            result = mermaid_tool._run(
                mermaid_code=diagram_spec.mermaid_code,
                output_path=diagram_path,
                theme="default"
            )


            
            # Add diagram path to response
            response_data["diagram_path"] = diagram_path
            
            # If the initial diagram generation failed, try with alternative diagram types
            if result.startswith("Error"):
                response_data["diagram_error"] = result
                
                # Define all possible diagram types to try
                all_diagram_types = ["flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", 
                                    "timeline", "pie", "blockDiagram", "gantt", "erDiagram"]
                
                # Remove the current diagram type from alternatives
                current_type = diagram_spec.diagram_type
                
                # Create list of alternative types: first remove current type and previously used types
                alternative_types = [t for t in all_diagram_types if t != current_type and t not in previously_drawn_diagrams]
                
                self.session.output_message.add(f"Initial diagram generation failed. Will try {len(alternative_types)} alternative diagram types.", level="warning")
                
                # Track if any alternative diagram succeeds
                alternative_success = False
                
                # Try each alternative diagram type until one succeeds
                for alt_type in alternative_types:
                    try:
                        self.session.output_message.add(f"Trying with {alt_type} diagram...", level="info")
                        
                        # Create a new prompt specifying this alternative type
                        alternative_prompt = self._get_prompt(
                            section=section, 
                            slide=slide, 
                            additional_data=f"IMPORTANT: Plese fix invalid syntax in the diagram code if cannot fix you can create new diagram with the same content with type {alt_type}. Prefer fix syntax with error {result}.",
                       )
                        
                        # Get response for alternative diagram
                        self.session.save_prompt(key=section.section_index, type="diagram", prompt=formatted_prompt)
                        alternative_response = self.llm.invoke(alternative_prompt)
                        
                        # Parse the response to get the alternative diagram specification
                        alternative_spec : DiagramSpec = self.output_parser.invoke(alternative_response)
                        
                        # Try to generate the alternative diagram
                        alternative_result = mermaid_tool._run(
                            mermaid_code=alternative_spec.mermaid_code,
                            output_path=diagram_path,
                            theme="default"
                        )
                        
                        if not alternative_result.startswith("Error"):
                            # This alternative worked! Update the diagram spec and break the loop
                            diagram_spec = alternative_spec
                            response_data = diagram_spec.model_dump()
                            response_data["diagram_path"] = diagram_path
                            self.session.output_message.add(f"Successfully generated alternative {diagram_spec.diagram_type} diagram.", level="info")
                            logger.info(f"Successfully generated alternative diagram and saved to {diagram_path}")
                            alternative_success = True
                            
                            # Add this successful diagram type to previously drawn diagrams
                            if alt_type not in previously_drawn_diagrams:
                                previously_drawn_diagrams.append(alt_type)
                            
                            break
                        else:
                            # Log failure for this alternative
                            logger.info(f"Alternative diagram type {alt_type} also failed: {alternative_result}")
                    
                    except Exception as alt_error:
                        # Log error for this alternative
                        logger.error(f"Error with alternative diagram type {alt_type}: {str(alt_error)}")
                
                # If all alternatives failed, add comprehensive error message
                if not alternative_success:
                    error_message = f"Failed to generate diagram with initial type '{current_type}' and all alternative types"
                    self.session.output_message.add(error_message, level="error")
                    response_data["diagram_error"] = error_message
            else:
                # Original diagram generation succeeded
                logger.info(f"Successfully generated diagram and saved to {diagram_path}")
                
                # Add this successful diagram type to previously drawn diagrams
                if diagram_spec.diagram_type not in previously_drawn_diagrams:
                    previously_drawn_diagrams.append(diagram_spec.diagram_type)
            
            # Update the session state with the updated list of previously drawn diagrams
            self.session.state.requirements["diagram_drawed"] = previously_drawn_diagrams
            
            # Store diagram information in session drafts
            self.session.add_draft(
                agent_name=self.agent_name,
                step="image_create_diagram_specs",
                content={
                    "diagram_type": diagram_spec.diagram_type,
                    "diagram_spec": diagram_spec.mermaid_code,
                    "diagram_path": response_data.get("diagram_path", ""),
                    "previously_drawn_diagrams": previously_drawn_diagrams
                },
            )
            
            # Save drafts to file
            self.session.save_drafts_to_json("drafts.json")
            
            # Return successful response
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully generated diagram specification",
                data=response_data,
                metadata={}
            )
        
        except Exception as e:
            # Log error
            logger.error(f"Failed to generate diagram specification: {str(e)}")
            
            # Return error response
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to generate diagram specification: {str(e)}",
                data={"raw_response": response if 'response' in locals() else "No response generated"}
            )
