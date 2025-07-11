"""
Implementation of the Slide Content Agent, responsible for generating content for multiple slides per section.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from core_ai.libs.core.base_agent import BaseAgent
from core_ai.libs.core.agent_response import AgentResponse
from core_ai.libs.core.agent_status import AgentStatus
from core_ai.libs.core.session import Session, Outline, Section
from core_ai.libs.models.slide_models import SectionContent, SlideContent
import json
from core_ai.libs.utils.content_llm import json_to_readable_str

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
        outline: Outline,
        section: Section,
        section_index: int,
    ) -> Tuple[PromptTemplate, Dict[str, Union[str, int]]]:
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
        research_content = self.session.get_research_content()

        if research_content:
            self.session.output_message.add(
                f"🔬 Using research content ({len(research_content)} chars) for enhanced slide generation", 
                level="info"
            )
        else:
            self.session.output_message.add(
                f"📊 No research data found, proceeding without it", 
                level="info"
            )

        self.session.output_message.add(
            f"Generating content for section slides...", 
            level="info"
        )

        inputs = {
            "topic": topic or "Unknown topic",
            "presentation_title": presentation_title or "Untitled Presentation",
            "audience": audience or "General audience",
            "purpose": purpose or "Informational",
            "data": json_to_readable_str(outline.model_dump(), section.model_dump()),
            "research_content": research_content or "",  
            "estimated_slides": section.estimated_slides,
            "format_instructions": self.output_parser.get_format_instructions(),
            "chapter_number": self.convert_section_index_to_chapter_number(
                section_index
            ),
            "section_type": section.section_type or "section",
        }

        format_instructions = self.output_parser.get_format_instructions()
        formatted_prompt = self.section_prompt.partial(
            format_instructions=format_instructions
        ).format(**inputs)

        return formatted_prompt, inputs
    

    def run(self, section_index: int, agent_index: int = 0) -> AgentResponse:
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
                section=section,
                section_index=section_index,
            )

            if self.session.has_research_content():
                logger.info(f"Section #{section_index}: Using research-enhanced content generation")
            else:
                logger.info(f"Section #{section_index}: Using standard content generation")

            self.session.save_prompt(
                key=section_index, type="slide_content", prompt=formatted_prompt
            )
            # Get response from LLM using invoke()
            response = self.llm.invoke(formatted_prompt)

            # Parse the response
            parsed_content: SectionContent = self.output_parser.invoke(response)

            # Clean the parsed content to remove special characters generated by LLM
            cleaned_slides = [slide.clean() for slide in parsed_content.slides]
            parsed_content.slides = cleaned_slides

            # Log success
            logger.info(
                f"Successfully generated content for section: #{section_index} - {section.section_type}"
            )

            def dump_result(index: int, slide: SlideContent) -> Dict[str, Any]:
                result = slide.model_dump()
                result["slide_index"] = index
                result["section_index"] = section_index
                if section_index >= 2 and index == 0 and len(result["keywords"]) == 0:
                    result["content"] = f"{section_index - 1:02d}"

                # if section_index == 1 and index == 0:
                #     number_content = []
                #     for i, content in enumerate(result["content"]):
                #         number_content.append(f"{i + 1:02d}. {content}")
                #     result["content"] = number_content

                return result

            data_save = [
                dump_result(index, slide)
                for index, slide in enumerate(parsed_content.slides)
            ]

            # Return successful response
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully generated {len(parsed_content.slides)} slides for section: #{section_index}",
                data={
                    "slides": data_save,
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to generate slide content for section #{section_index}: {str(e)}"
            )

            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to generate slide content #{section_index}: {str(e)}",
                data={"error": str(e)},
            )

    def convert_section_index_to_chapter_number(self, section_index: int) -> str:
        """
        Convert section index to chapter number format (01, 02, etc.).

        Args:
            section_index: Index of the section

        Returns:
            Formatted chapter number as a string
        """
        return f"{section_index - 1:02d}"

    def edit_slide_content(
        self, section, current_slide, edit_prompt: str
    ) -> AgentResponse:
        """
        Edit existing slide content based on user prompt.

        Args:
            section: Section information
            current_slide: Current slide to be edited
            edit_prompt: User's edit instructions

        Returns:
            AgentResponse with edited slide content
        """
        try:
            formatted_prompt = self._get_edit_prompt(
                section, current_slide, edit_prompt
            )
            self.session.save_prompt(
                key=f"edit_{current_slide.section_index}_{current_slide.slide_index}",
                type="slide_edit",
                prompt=formatted_prompt,
            )
            response = self.llm.invoke(formatted_prompt)
            parsed_content = self.output_parser.invoke(response)

            # Clean the parsed content to remove special characters generated by LLM
            cleaned_slides = [slide.clean() for slide in parsed_content.slides]
            parsed_content.slides = cleaned_slides

            edited_slide = parsed_content.slides[0] if parsed_content.slides else None

            if not edited_slide:
                return AgentResponse(
                    status=AgentStatus.ERROR,
                    message="Failed to generate edited slide content",
                    data={"error": "No slides generated from edit prompt"},
                )

            edited_data = {
                "title": edited_slide.title,
                "content": edited_slide.content,
                "notes": edited_slide.notes,
                "keywords": edited_slide.keywords,
                "section_index": current_slide.section_index,
                "slide_index": current_slide.slide_index,
            }

            logger.info(
                f"Successfully edited slide content for slide {current_slide.slide_index} in section {current_slide.section_index}"
            )

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully edited slide content",
                data=edited_data,
            )
        except Exception as e:
            logger.error(f"Failed to edit slide content: {str(e)}")
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to edit slide content: {str(e)}",
                data={"error": str(e)},
            )

    def _get_edit_prompt(self, section, current_slide, edit_prompt: str) -> str:
        """
        Create edit-specific prompt.

        Args:
            section: Section information
            current_slide: Current slide data
            edit_prompt: User's edit instructions

        Returns:
            Formatted prompt for editing
        """
        format_instructions = self.output_parser.get_format_instructions()
        edit_template = """
You are an expert presentation content editor. Your task is to modify an existing slide based on user instructions.

**CURRENT SLIDE INFORMATION:**
Section Title: {section_title}
Section Type: {section_type}
Current Slide Title: {current_title}
Current Slide Content: {current_content}
Current Speaker Notes: {current_notes}
Current Keywords: {current_keywords}

**EDIT INSTRUCTIONS:**
{edit_prompt}

**TASK:**
Modify the slide content based on the edit instructions while maintaining:
1. Consistency with the overall presentation theme
2. Appropriate content structure for the section type
3. Professional presentation style

Generate exactly 1 slide with the requested modifications.

**OUTPUT FORMAT:**
Follow the same format as regular slide generation but ensure the modifications requested are applied.

{format_instructions}
"""

        formatted_prompt = edit_template.format(
            section_title=section.title,
            section_type=section.section_type,
            current_title=current_slide.content.get("title", ""),
            current_content=current_slide.content.get("content", ""),
            current_notes=current_slide.content.get("notes", ""),
            current_keywords=current_slide.content.get("keywords", []),
            edit_prompt=edit_prompt,
            format_instructions=format_instructions,
        )

        return formatted_prompt


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
        section_type="section",
    )

    print(response)
