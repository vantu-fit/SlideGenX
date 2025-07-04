"""
Slide Edit Orchestrator for editing specific slides in a presentation.
"""

import logging
import os

from typing import Dict, Any, Optional
from core_ai.libs.core.session import Session
from core_ai.libs.core.agent_response import AgentResponse
from core_ai.libs.core.agent_status import AgentStatus
from core_ai.libs.agents.slide_content_agent.agent import SlideContentAgent
from core_ai.libs.agents.slide_generator_agent.agent import SlideGeneratorAgent
from core_ai.libs.config import TreeOfThoughtConfig
from core_ai.libs.utils.merge_pptx import merge_pptx_files

logger = logging.getLogger(__name__)

class SlideEditOrchestrator:
    """Orchestrator for editing specific slides in a presentation."""
    
    def __init__(self, session: Session, config: Optional[TreeOfThoughtConfig] = None):
        self.session = session
        self.config = config or TreeOfThoughtConfig()
        
    def edit_slide(
        self, 
        section_index: int, 
        slide_index: int, 
        edit_prompt: str,
        merge_output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit a specific slide based on user prompt.
        
        Args:
            section_index: Index of the section containing the slide
            slide_index: Index of the slide within the section
            edit_prompt: User's edit instructions
            
        Returns:
            Dictionary with edit results
        """
        try:
            # Validate indices
            if not self._validate_indices(section_index, slide_index):
                return {
                    "status": "error",
                    "message": "Invalid section or slide index",
                    "data": {}
                }
            
            # Get current slide
            current_slide = self.session.get_slide_by_indices(section_index, slide_index)
            current_section = self.session.memory.get_session_by_index(section_index)
            
            if not current_slide or not current_section:
                return {
                    "status": "error",
                    "message": "Slide or section not found",
                    "data": {}
                }
            
            self.session.output_message.add(
                f"Starting edit for slide {slide_index} in section {section_index}",
                level="info"
            )
            
            # Step 1: Generate new content using SlideContentAgent
            new_content_response = self._generate_edited_content(
                current_section, current_slide, edit_prompt
            )
            
            if not new_content_response or new_content_response.status != AgentStatus.SUCCESS:
                return {
                    "status": "error",
                    "message": "Failed to generate new slide content",
                    "data": {}
                }
            
            # Step 2: Generate new slide using SlideGeneratorAgent
            new_slide_response = self._regenerate_slide(
                section_index, slide_index, new_content_response.data
            )
            
            if not new_slide_response or new_slide_response.status != AgentStatus.SUCCESS:
                return {
                    "status": "error", 
                    "message": "Failed to generate new slide",
                    "data": {}
                }
            
            # Step 3: Update session memory
            self._update_session_memory(section_index, slide_index, new_content_response.data)
            
            self.session.output_message.add(
                f"Successfully edited slide {slide_index} in section {section_index}",
                level="info"
            )

            # Step 4: Merge slides if output path is provided
            merged_path = None
            if merge_output_path:
                try:
                    merge_pptx_files(
                        input_dir=self.session.memory.slide_temp_path, 
                        output_path=merge_output_path
                    )
                    merged_path = merge_output_path

                    self.session.output_message.add(
                        f"Successfully merged slides into {merge_output_path}",
                        level="info"
                    )
                except Exception as e:
                    logger.error(f"Error merging slides: {str(e)}")
                    self.session.output_message.add(
                        f"Failed to merge slides: {str(e)}",
                        level="error"
                    )
            
            return {
                "status": "success",
                "message": "Slide edited successfully",
                "data": {
                    "section_index": section_index,
                    "slide_index": slide_index,
                    "new_content": new_content_response.data,
                    "slide_path": new_slide_response.data.get("prs"),
                    "merged_presentation_path": merged_path
                }
            }
            
        except Exception as e:
            logger.error(f"Error editing slide: {str(e)}")
            return {
                "status": "error",
                "message": f"Error editing slide: {str(e)}",
                "data": {}
            }
    
    def _validate_indices(self, section_index: int, slide_index: int) -> bool:
        """Validate section and slide indices."""
        print(f"Validating indices: section_index={section_index}, slide_index={slide_index}")
        print(f"Total sections: {self.session.memory.outline.num_sections}")

        if section_index < 0 or section_index >= self.session.memory.outline.num_sections:
            print(f"Invalid section index: {section_index}")
            return False
        
        section_slides = self.session.memory.get_slides_by_section_index(section_index)
        print(f"Slides in section {section_index}: {len(section_slides) if section_slides else 0}")

        if not section_slides or slide_index < 0 or slide_index >= len(section_slides):
            print(f"Invalid slide index: {slide_index} for section {section_index}")
            return False
            
        return True
    
    def _generate_edited_content(self, section, slide, edit_prompt) -> Optional[AgentResponse]:
        """Generate new slide content based on edit prompt."""
        slide_content_agent = SlideContentAgent(session=self.session)
        
        # Create a modified version of SlideContentAgent for editing
        response = slide_content_agent.edit_slide_content(
            section=section,
            current_slide=slide,
            edit_prompt=edit_prompt
        )
        
        return response
    
    def _regenerate_slide(self, section_index: int, slide_index: int, new_content: Dict) -> Optional[AgentResponse]:
        """Regenerate slide with new content."""
        slide_generator_agent = SlideGeneratorAgent(session=self.session)
        
        # Update the slide in memory temporarily for generation
        self._update_session_memory(section_index, slide_index, new_content)
        
        # Generate the slide
        response = slide_generator_agent.run(section_index=section_index, agent_index=slide_index)
        
        return response
    
    def _update_session_memory(self, section_index: int, slide_index: int, new_content: Dict):
        """Update session memory with new slide content."""
        # Update the specific slide in memory
        slides = self.session.memory.get_slides_by_section_index(section_index)
        if slides and slide_index < len(slides):
            current_content = slides[slide_index].content
            # Update slide content
            current_content['title'] = new_content.get("title", current_content.get("title", ""))
            current_content['content'] = new_content.get("content", current_content.get("content", ""))
            current_content['notes'] = new_content.get("notes", current_content.get("notes", ""))
            current_content['keywords'] = new_content.get("keywords", current_content.get("keywords", []))

            # Save updated memory
            self.session.memory.save_to_json("memory.json")
