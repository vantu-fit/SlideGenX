"""
Implementation of the Outline Agent, responsible for creating presentation outlines.
Using the LangChain chain pattern while inheriting from BaseAgent.
"""

import logging
from typing import Dict, Any, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from core_ai.libs.core.base_agent import BaseAgent
from core_ai.libs.core.agent_response import AgentResponse
from core_ai.libs.core.agent_status import AgentStatus
from core_ai.libs.core.session import Session, CLassifyLayout
from core_ai.libs.models.outline_models import PresentationOutline
from core_ai.libs.agents.slide_generator_agent.slide_handler import SlideHandler

from .prompts import outline_prompt, outline_variation_prompt, outline_with_context_prompt, classify_layout_prompt
logger = logging.getLogger(__name__)

class OutlineInput(BaseModel):
    """Input for the outline chain"""
    topic: str = Field(..., description="Main topic of the presentation")
    audience: str = Field(..., description="Target audience")
    duration: int = Field(..., description="Duration in minutes")
    purpose: str = Field(..., description="Purpose (inform, persuade, educate)")
    context: Optional[str] = Field(None, description="Optional industry context")
    brand_guidelines: Optional[str] = Field(None, description="Optional brand guidelines")
    original_outline: Optional[Dict[str, Any]] = Field(None, description="Optional original outline")

class OutlineAgent(BaseAgent):
    """Agent responsible for creating presentation outlines."""
    
    agent_name = "outline_agent"
    description = "Creates overall presentation outlines based on a given topic and requirements."
    
    def __init__(self, session: Session, **kwargs):
        """
        Initialize the Outline Agent.
        
        Args:
            session: The current session
            **kwargs: Additional keyword arguments
        """
        super().__init__(session, **kwargs)

        self.output_parser = PydanticOutputParser(pydantic_object=PresentationOutline)
        
        # Base outline chain prompt
        self.base_prompt = outline_prompt
        
        # Context chain prompt (with additional context/brand guidelines)
        self.context_prompt = outline_with_context_prompt
        
        # Variation chain prompt (creates variation of existing outline)
        self.variation_prompt = outline_variation_prompt

        self.classify_layout_prompt = classify_layout_prompt

    def classify_layout(self):
        """
        Classify the layout of the presentation slides.
        
        Returns:
            str: JSON string with classified layout information
        """
        if self.session.memory.slide_layouts:
            logger.info("Slide layouts already classified.")
            return self.session.memory.slide_layouts
        output_parser = PydanticOutputParser(pydantic_object=CLassifyLayout)
        format_instructions = output_parser.get_format_instructions()
        layout_tool = SlideHandler(template_path=self.session.memory.user_input.template_path)
        inputs = {
            "layout_information" : layout_tool.to_llm()
        }
        self.session.memory.slide_layout_txt = layout_tool.to_llm()
        formatted_prompt = self.classify_layout_prompt.partial(
            format_instructions=format_instructions
        ).format(**inputs)
        print(formatted_prompt)
        try:
            self.session.save_prompt(key=1, type="outline", prompt=formatted_prompt)
            response = self.llm.invoke(formatted_prompt)
            parsed_response : CLassifyLayout = output_parser.invoke(response)
            self.session.memory.slide_layouts = parsed_response
            return parsed_response.model_dump()
        except Exception as e:
            logger.error(f"Failed to classify layout: {str(e)}")
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to classify layout: {str(e)}",
                data={"error": str(e)}
            )

    def _get_prompt_and_inputs(self, topic, audience, duration, purpose, context, brand_guidelines, original_outline):
        """
        Determine which prompt to use and prepare the inputs.
        
        Returns:
            tuple: (prompt, inputs)
        """
        # Common inputs for all prompts
        inputs = {
            "topic": topic,
            "audience": audience,
            "duration": duration,
            "purpose": purpose,
            "format_instructions": self.output_parser.get_format_instructions()
        }
        
        # Determine which prompt to use based on inputs
        if original_outline:
            self.session.output_message.add("Generating outline variation...", level="info")
            prompt = self.variation_prompt
            inputs["original_outline"] = str(original_outline)
        elif context or brand_guidelines:
            self.session.output_message.add("Generating outline with context...", level="info")
            prompt = self.context_prompt
            inputs["context"] = context or "Not specified"
            inputs["brand_guidelines"] = brand_guidelines or "Not specified"
        else:
            self.session.output_message.add("Generating outline...", level="info")
            prompt = self.base_prompt
        
        return prompt, inputs
    
    def run(self, topic: str, audience: str, duration: int, purpose: str, 
            context: str = None, brand_guidelines: str = None,
            original_outline: Dict[str, Any] = None) -> AgentResponse:
        """
        Generate a presentation outline.
        
        Args:
            topic: The main topic of the presentation
            audience: The target audience (e.g., "executives", "technical team", "general public")
            duration: Presentation duration in minutes
            purpose: Purpose of the presentation (e.g., "inform", "persuade", "educate")
            context: Optional industry/context information
            brand_guidelines: Optional brand guidelines
            original_outline: Optional original outline for creating variations
        
        Returns:
            AgentResponse containing the presentation outline
        """
        classify_layout = self.classify_layout()
        try:
            # Get appropriate prompt and inputs
            prompt, inputs = self._get_prompt_and_inputs(
                topic, audience, duration, purpose, context, brand_guidelines, original_outline
            )
            
            # Call LLM
            formatted_prompt = prompt.format_prompt(**inputs).to_string()
            self.session.save_prompt(key=1, type="outline", prompt=formatted_prompt)
            response = self.llm.invoke(formatted_prompt)
            
            # Parse the response
            parsed_outline : PresentationOutline = self.output_parser.invoke(response)
            
            # Log 
            logger.info(f"Successfully generated outline with {len(parsed_outline.sections)} sections")
            
            # Save to Draft
            self.session.add_draft(
                agent_name=self.agent_name,
                step="outline",
                content=parsed_outline.model_dump(),
            )
            self.session.save_drafts_to_json("drafts.json")
            
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                message=f"Successfully generated outline with {len(parsed_outline.sections)} sections",
                data=parsed_outline.model_dump(),
                metadata={
                    "topic": topic,
                    "audience": audience,
                    "duration": duration,
                    "purpose": purpose,
                    "num_sections": len(parsed_outline.sections),
                    "total_slides": parsed_outline.total_slides
                }
            )
        except Exception as e:
            # Log error
            logger.error(f"Failed to generate outline: {str(e)}")
            
            # Return error response
            return AgentResponse(
                status=AgentStatus.ERROR,
                message=f"Failed to generate outline: {str(e)}",
                data={"error": str(e)}
            )
        
