

"""
Implementation of the Slide Generator Agent, responsible for integrating all elements into a final slide.
"""

import logging
from typing import List, Dict, Any, Optional
import os, datetime
from pptx import Presentation
from .schemas import PresentationContent, RefitContent
from libs.utils.pptx2pdf import convert_to_pdf
import json
from libs.core.base_agent import BaseAgent
from libs.core.agent_response import AgentResponse
from libs.core.agent_status import AgentStatus
from libs.core.session import Session, Slide, Section
from .prompts import (
    choose_layout_prompt,
    try_other_layout_prompt,
    fit_content_prompt,
    choose_layout_chapter_prompt,
)
from langchain.output_parsers import PydanticOutputParser




from .schemas import ChooseLayout, SlideMapping

from .tools import MasterSlideTool
from .slide_handler import SlideHandler

from libs.agents.diagram_agent.agent import DiagramAgent
from libs.agents.image_agent.agent import ImageAgent

logger = logging.getLogger(__name__)

class SlideGeneratorAgent(BaseAgent):
    """Agent responsible for integrating all elements and generating the final slide."""
    
    agent_name = "slide_generator_agent"
    description = "Integrates content, images, diagrams, and styling to create the final slide."
    
    def __init__(self, session: Session, **kwargs):
        """
        Initialize the Slide Generator Agent.
        
        Args:
            session: The current session
            **kwargs: Additional keyword arguments
        """
        # Call parent constructor - no specific output parser as this produces formatted text
        super().__init__(session, **kwargs)
        
        # Initialize prompt templates
        self.choose_layout_prompt = choose_layout_prompt
        self.fit_placeholder_prompt = fit_content_prompt
        self.try_orther_layout_prompt = try_other_layout_prompt
        self.choose_layout_chapter_prompt = choose_layout_chapter_prompt

        self.diagram_agent = DiagramAgent(session=self.session, **kwargs)
        self.image_agent = ImageAgent(session=self.session, **kwargs)
        

        self.tools = {
            "slide_handler" : SlideHandler(template_path=self.session.memory.user_input.template_path)
        }

    
    def _get_choose_layout_prompt(self, section: Section, slides: List[Slide], previous_layouts : List[int]):
        output_parser = PydanticOutputParser(pydantic_object=ChooseLayout)
        section_data = section.model_dump()
        del section_data['section_index']
        slide_data = [slide.model_dump() for slide in slides]
        for slide in slide_data:
            del slide['section_index']
            del slide['slide_index']
            del slide['path']
            del slide['content']['layout_type']
            del slide['content']['layout']
        if not previous_layouts:
            format_instructions = output_parser.get_format_instructions()
            indexs = None
            chapter_title_indexs = None
            if self.session.memory.slide_layouts:
                layout_data = self.session.memory.slide_layouts.model_dump()
                section_type = section.section_type
                if section_type in layout_data:
                    if section_type == "chapter":
                        chapter_title_indexs = layout_data["chapter_title"]
                        indexs = layout_data[section_type]
                    else:
                        indexs = layout_data[section_type]

            if chapter_title_indexs:     
                section_str = f"""
                Title: {section_data['title']}
                Description: {section_data['description']}
                Key Points: {section_data['key_points']}
                Estimated Slides: {section_data['estimated_slides']}
                Section Type: {section_data['section_type']}
                """
                
                slides_str = "\n".join([
                    f"""
                    Title: {slide['content']['title']}
                    Content: {slide['content']['content']}
                    Notes: {slide['content']['notes']}
                    Keywords: {slide['content']['keywords']}
                    {f"Images: {slide['images']}" if slide['images'] else ""} 
                    {f"Images: {slide['diagrams']}" if slide['diagrams'] else ""} 
                    """ for slide in slide_data
                ])
                
                inputs = {
                    "section": section_str,
                    "slides": slides_str,
                    "chapter_slide": self.tools.get("slide_handler").to_llm(indexs=chapter_title_indexs),
                    "layout_information": self.tools.get("slide_handler").to_llm(indexs=indexs),
                }

                formatted_prompt = self.choose_layout_chapter_prompt.partial(
                    format_instructions=format_instructions
                ).format(**inputs)
                return output_parser, formatted_prompt
            elif indexs:
                section_str = f"""
                Title: {section_data['title']}
                Description: {section_data['description']}
                Key Points: {section_data['key_points']}
                Estimated Slides: {section_data['estimated_slides']}
                Section Type: {section_data['section_type']}
                """
                
                slides_str = "\n".join([
                    f"""
                    Title: {slide['content']['title']}
                    Content: {slide['content']['content']}
                    Notes: {slide['content']['notes']}
                    Keywords: {slide['content']['keywords']}
                    {f"Images: {slide['images']}" if slide['images'] else ""} 
                    {f"Images: {slide['diagrams']}" if slide['diagrams'] else ""} 
                    """ for slide in slide_data
                ])
                
                inputs = {
                    "section": section_str,
                    "slides": slides_str,
                    "layout_information": self.tools.get("slide_handler").to_llm(indexs=indexs),
                }

                formatted_prompt = self.choose_layout_prompt.partial(
                    format_instructions=format_instructions
                ).format(**inputs)
                return output_parser, formatted_prompt
        else:
            format_instructions = output_parser.get_format_instructions()
            inputs = {
                "section": json.dumps(section_data, indent=2),
                "slides": json.dumps(slide_data, indent=2),
                "layout_information": self.tools.get("slide_handler").to_llm(),
                "previous_layouts" : previous_layouts
            }

            formatted_prompt = self.choose_layout_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
                
        return output_parser, formatted_prompt

    def fit_content(self, section: Section, slides: List[Slide], layout_indexs: List[int]) -> AgentResponse:
        """
        Fit the content into the selected layout and generate the final slide.
        
        Args:
            section: Section information
            slides: List of slide data
            layout_indexs: List of layout indices to use for each slide
            
        Returns:
            AgentResponse with the generated slide content
        """
        layouts = self.tools.get("slide_handler").to_llm_json(layout_indexs)
        
        output_parser = PydanticOutputParser(pydantic_object=SlideMapping)
        format_instructions = output_parser.get_format_instructions()

        slides = [slide.model_dump() for slide in slides]
        section = section.model_dump()
        def merge_inputs(layout, slide):
            del slide['section_index']
            del slide['slide_index']
            del slide['path']

            slide['layout'] = layout
            return slide
        
        input_merged = [merge_inputs(layout, slide) for layout, slide in zip(layouts, slides)]
        
        format_instructions = output_parser.get_format_instructions()
        section_str = f"""
            Title: {section['title']}
            Estimated Slides: {section['estimated_slides']}
            Section Type: {section['section_type']}
        """

        slides_str = "\n".join([
            f"""
            Title: {slide['content']['title']}
            Content: {slide['content']['content']}
            Keywords: {slide['content']['keywords']}
            {f"Images: {slide['images']}" if slide['images'] else ""} 
            {f"Images: {slide['diagrams']}" if slide['diagrams'] else ""} 
            Layout: {json.dumps(slide['layout'], indent=2)}
            """ for slide in input_merged
        ])

        inputs = {
            "section" : section_str,
            "inputs": slides_str,
            "sample": json.dumps({"slides": [{"mappings": {"2": "Introduction", "1": ["Point 1", "Point 2"]}}]}),
        }

        formatted_prompt = self.fit_placeholder_prompt.partial(
            format_instructions=format_instructions
        ).format(**inputs)
        
        self.session.save_prompt(key=section["section_index"], type="fit_content", prompt=formatted_prompt)
        response = self.llm.invoke(formatted_prompt)
        
        def create_map(slide, layout_index):
            mapping = slide.mappings
            mapping["layout_index"] = layout_index
            return mapping
        parsed_spec = output_parser.invoke(response)
        slides = parsed_spec.slides
        mappings = [create_map(slide, layout_index) for slide, layout_index in zip(slides , layout_indexs)]
        return mappings
        

    def mapping_to_presentation_content(self, section_index: int,  mappings: List[Dict], save_path : str) -> PresentationContent:
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        # init image, diagram
        for slide_index, slide in enumerate(mappings):
            for placeholder_idx, content in slide.items():
                if isinstance(content, str):
                    if content.endswith(".png") or content.endswith(".jpg"):
                        if "diagram" in content:
                            digram_response = self.diagram_agent.run(
                                section_index=section_index, 
                                slide_index=slide_index, 
                                diagram_path=content, 
                            )
                            logger.info(f"DIGRAM: {digram_response}")
                        if "image" in content:
                            image_response = self.image_agent.run(
                                section_index=section_index,
                                slide_index=slide_index,
                                image_path=content
                            )
                            logger.info(f"IMAGE: {image_response}")
        output_parser = PydanticOutputParser(pydantic_object=RefitContent)
        format_instructions = output_parser.get_format_instructions()
        result = self.tools.get("slide_handler").create_slides(mappings, return_prs=True, output_path=save_path)
        retry = 3
        def check_result(result):
            for map in result:
                if map != []:
                    return True
            return False
        
        # Autofit Text
        while check_result(result[0]) and retry > 0:
            retry -= 1
            try:
                prompt = self.tools.get("slide_handler").resutl_to_llm(result[0])
                prompt += format_instructions
                self.session.save_prompt(key=section_index, type="mapping", prompt=prompt)
                response = self.llm.invoke(prompt)
                parsed_spec : RefitContent = output_parser.invoke(response)
                for content_refit, mapping in zip(parsed_spec.contents, mappings):
                    if content_refit.slide_content:
                        for placeholder in content_refit.slide_content:
                            mapping[str(placeholder.placeholder)] = placeholder.content

                result = self.tools.get("slide_handler").create_slides(mappings, return_prs=True, output_path=save_path)
            except Exception as e:
                print(f"Error: {e}")

        # Auto fit image
        # retry = 3
        # while check_result(result[1]) and retry > 0:
        #     retry -= 1
        #     try:   
        #         prompt = self.tools.get("slide_handler").result_visual_to_llm(result[1])
                
        #         for prompt, result in zip(prompt, result[1]):
        #             if result == []:
        #                 continue
        #             if result["type"] == "diagram":
        #                 diagram_response = self.diagram_agent.run(
        #                     section_index=section_index, 
        #                     slide_index=result["slide_index"], 
        #                     diagram_path=result["path"], 
        #                     additional_data=prompt
        #                 )
        #                 if diagram_response.status == AgentStatus.SUCCESS:
        #                     self.session.output_message.add(
        #                     f"Successfully create digram for section #{section_index}",
        #                     level="info")
        #                 else:
        #                     self.session.output_message.add(
        #                     f"Failed to create diagram for section #{section_index}",
        #                     level="error")
        #             if result["type"] == "image":
        #                 image_response = self.image_agent.run(
        #                     section_index=section_index, 
        #                     slide_index=result["slide_index"], 
        #                     image_path=result["path"], 
        #                     additional_data=prompt
        #                 )
        #                 if image_response.status == AgentStatus.SUCCESS:
        #                     self.session.output_message.add(
        #                     f"Successfully create image for section #{section_index}",
        #                     level="info")
        #                 else:
        #                     self.session.output_message.add(
        #                     f"Failed to create image for section #{section_index}",
        #                     level="error")
                        
            
                
                    # result = self.tools.get("slide_handler").create_slides(mappings, return_prs=True, output_path=save_path) 
            except Exception as e:
                print(f"Error: {e}")
        return {
            "section_index" : section_index,
            "prs" : result[2]   
        }
        

    def run(self, section_index : int, agent_index : int) -> AgentResponse:
        """
        Run the agent to generate slides based on the provided section and slide data.
        
        Args:
            section: Section information
            slides: List of slide data
            
        Returns:
            AgentResponse with information about generated slides
        """
        
        # try:
        slides = self.session.memory.get_slides_by_section_index(section_index=section_index)
        section = self.session.memory.get_session_by_index(index=section_index)

        layout_indexs = self.choose_layout(section, slides)
        
        content_mapping = self.fit_content(section, slides, layout_indexs)
        
        prs = self.mapping_to_presentation_content(section_index=section_index, mappings=content_mapping, save_path=slides[0].path)
        return AgentResponse(
            status=AgentStatus.SUCCESS,
            message=f"Successfully generated slides for section #{section_index}",
            data={
                "prs" : prs
            },
        )

    def choose_layout(self, section: Section, slides: List[Slide], previous_layouts : List[int] = []) -> list[int]:
        """
        """
        output_parser, formatted_prompt = self._get_choose_layout_prompt(section, slides, previous_layouts)
        # save prompt to file 
        if not os.path.exists("logs/slide_generator_agent"):
            os.makedirs("logs/slide_generator_agent")
        self.session.save_prompt(key=section.section_index, type="choose_layout", prompt=formatted_prompt)
        response = self.llm.invoke(formatted_prompt)
        parsed_spec = output_parser.invoke(response)

        return parsed_spec.slide_indexs
