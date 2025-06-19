"""
Implementation of the Slide Content Agent, responsible for generating content for multiple slides per section.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from libs.core.base_agent import BaseAgent
from libs.core.agent_response import AgentResponse
from libs.core.agent_status import AgentStatus
from libs.core.session import Session, Outline, Section
from libs.models.slide_models import SectionContent, SlideContent
import json
from libs.utils.content_llm import json_to_readable_str

from .prompts import section_slides_content_prompt

logger = logging.getLogger(__name__)


class SlideContentAgent(BaseAgent):
    """Agent responsible for generating detailed content for slides based on section information."""
    
    agent_name = "slide_content_agent"
    description = "Generates detailed content for slides based on the presentation outline and section information."
    
    def __init__(self, session: Session, **kwargs):
        """
        Initialize the Slide Content Agent.
        
        Args:
            session: The current session
            **kwargs: Additional keyword arguments
        """
        super().__init__(session, **kwargs)
        self.output_parser = PydanticOutputParser(pydantic_object=SectionContent) 
        
        # Create prompts for different slide types
        self.section_prompt = section_slides_content_prompt    
        
    def _get_prompt(
            self, 
            topic: str, 
            presentation_title: str, 
            audience: str, 
            purpose: str, 
            outline : Outline,
            section: Section) -> Tuple[PromptTemplate, Dict[str, Union[str, int]]]:
        """
        Determine which prompt to use and prepare the inputs.
        
        Args:
            topic: Topic of the presentation
            presentation_title: Title of the presentation
            audience: Audience for the presentation
            purpose: Purpose of the presentation
            outline: Outline of the presentation
            section: Section data to generate content for
            
        Returns:
            tuple: (prompt, inputs)
        """
        self.session.output_message.add(f"Generating content for section slides...", level="info")
        

        inputs = {
            "topic": topic or "Unknown topic",
            "presentation_title": presentation_title or "Untitled Presentation",
            "audience": audience or "General audience",
            "purpose": purpose or "Informational",
            "data": json_to_readable_str(outline.model_dump(), section.model_dump()),
            "estimated_slides": section.estimated_slides,
            "format_instructions": self.output_parser.get_format_instructions()
        }
        format_instructions = self.output_parser.get_format_instructions()

        formatted_prompt = self.section_prompt.partial(
            format_instructions=format_instructions
        ).format(**inputs)
        
        return formatted_prompt, inputs
    
    def run(self, section_index: int, agent_index : int = 0) -> AgentResponse:
        """
        Generate content for slides based on section information.
        
        Args:
            section_index: Index of the section to generate content for 
            
        Returns:
            AgentResponse containing the slide content
        """

        # Get the section data from the session memory
        topic = self.session.memory.user_input.topic
        presentation_title = self.session.memory.user_input.presentation_title
        audience = self.session.memory.user_input.audience
        purpose = self.session.memory.user_input.purpose

        outline = self.session.memory.outline
        section = self.session.memory.get_session_by_index(index=section_index)
            
        try:
            # Get appropriate prompt and inputs
            formatted_prompt, _ = self._get_prompt(
                topic=topic,
                presentation_title=presentation_title,
                audience=audience,
                purpose=purpose,
                outline=outline,
                section=section
            )

            self.session.save_prompt(key=section_index, type="slide_content", prompt=formatted_prompt)
            # Get response from LLM using invoke()
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the response
            parsed_content : SectionContent = self.output_parser.invoke(response)
            
            # Log success
            logger.info(f"Successfully generated content for section: #{section_index}")


            def dump_result(index : int, slide : SlideContent) -> Dict[str, Any]:
                result = slide.model_dump()
                result["slide_index"] = index
                result["section_index"] = section_index
                return result

            data_save =[dump_result(index, slide) for index, slide in enumerate(parsed_content.slides)]
            
            
            # Return successful response
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully generated {len(parsed_content.slides)} slides for section: #{section_index}",
                data={
                    "slides": data_save,
                },
            )
        except Exception as e:
            logger.error(f"Failed to generate slide content for section #{section_index}: {str(e)}")
            
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to generate slide content #{section_index}: {str(e)}",
                data={"error": str(e)}
            )
        
if __name__ == "__main__":
    # Example usage of the SlideContentAgent
    session = Session()
    agent = SlideContentAgent(session=session)
    
    # Example section data
    section_data = {
        "title": "Introduction to AI",
        "description": "An overview of artificial intelligence.",
        "key_points": ["Definition of AI", "History of AI", "Applications of AI"],
        "estimated_slides": 3,
        "section_id": "ai_intro",
        "notes": "This section introduces the concept of AI and its significance.",
    }
    
    response = agent.run(
        topic="Artificial Intelligence",
        presentation_title="The Future of AI",
        audience="Tech Enthusiasts",
        purpose="Inform and Educate",
        section=section_data,
        section_type="section"
    )
    
    print(response)
