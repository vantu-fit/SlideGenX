"""
Enhanced Implementation of the Image Agent with SearXNG tool integration.
"""

import logging
import os, json
import uuid
import requests
from typing import List, Dict, Any, Optional, Union
import shutil
from urllib.parse import urlparse

from langchain.output_parsers import PydanticOutputParser
from langchain.tools import BaseTool

from core_ai.libs.core.base_agent import BaseAgent
from core_ai.libs.core.agent_response import AgentResponse
from core_ai.libs.core.agent_status import AgentStatus
from core_ai.libs.core.session import Session, Section, Slide
from core_ai.libs.models.visualization_models import ListImageSpec
import core_ai.config.global_config as gcfg
from .prompts import general_prompt, refit_prompt

# Import the SearXNG tool
from .tools import create_searxng_image_search_tool

logger = logging.getLogger(__name__)


class ImageAgent(BaseAgent):
    """
    Enhanced Agent responsible for finding or suggesting appropriate images for slides,
    with integrated tools for image search and management.
    """

    agent_name = "enhanced_image_agent"
    description = "Suggests and retrieves appropriate images based on slide content using multiple image sources."

    def __init__(
        self,
        session: Session,
        searxng_instance: str = gcfg.GlobalConfig.SEARXNG_ENDPOINT,
        **kwargs,
    ):
        """
        Initialize the Enhanced Image Agent.

        Args:
            session: The current session
            searxng_instance: URL of the SearXNG instance for image search
            **kwargs: Additional keyword arguments
        """
        super().__init__(session, **kwargs)
        # Initialize the output parser for ImageSpec
        self.output_parser = PydanticOutputParser(pydantic_object=ListImageSpec)

        # Initialize prompt templates with format instructions
        format_instructions = self.output_parser.get_format_instructions()

        self.general_prompt = general_prompt
        self.refit_prompt = refit_prompt

        # Initialize tools
        self.tools = {}
        self._initialize_tools(searxng_instance)

    def _initialize_tools(self, searxng_instance: str) -> None:
        self.tools["searxng_image_search"] = create_searxng_image_search_tool(
            searxng_instance=searxng_instance
        )

        logger.info(f"Initialized {len(self.tools)} image tools")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        return self.tools.get(tool_name)

    def _get_prompt(
        self,
        section: Section,
        slide: Slide,
        additional_data: str = None,
        previously_used_diagram_types: List[str] | None = None,
    ) -> str:
        """
        Prepare the prompt for generating diagram specifications.

        Args:
            section: The section data
            slide: The slide data

        Returns:
            The formatted prompt string
        """
        section_data = section.model_dump()
        del section_data["section_index"]
        slide_data = slide.model_dump()
        del slide_data["section_index"]
        del slide_data["slide_index"]
        del slide_data["path"]
        del slide_data["content"]["layout_type"]
        del slide_data["content"]["layout"]
        format_instructions = self.output_parser.get_format_instructions()
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
            Images: {slide_data['images']}
            Diagrams: {slide_data['diagrams']}
            """

            inputs = {
                "section": section_str,
                "slide": slide_str,
                "additional_data": additional_data,
            }
            formatted_prompt = self.refit_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt
        else:
            inputs = {
                "section": json.dumps(section_data, indent=2),
                "slide": json.dumps(slide_data, indent=2),
            }
            formatted_prompt = self.general_prompt.partial(
                format_instructions=format_instructions
            ).format(**inputs)
            return formatted_prompt

    def run(
        self,
        section_index: int,
        slide_index: int,
        image_path: str,
        additional_data: str | None = None,
        search_images: bool = True,
        num_images: int = 1,
        max_retries: int = 5,
    ) -> AgentResponse:
        logger.info(
            f"INPUT IMAGE AGENT: Generate image section: {section_index} - slide #{slide_index} - additional_data: {additional_data}"
        )
        """
        Generate image specifications for a slide and optionally search for matching images.
        
        Args:
            slide_title: The title of the slide
            slide_content: The content of the slide
            slide_purpose: The purpose of this specific slide
            image_descriptions: Optional explicit descriptions of images
            brand_guidelines: Optional brand guidelines
            search_images: Whether to perform image search after generating specs
            num_images: Number of images to search for (default: 3)
            max_retries: Maximum number of retry attempts (default: 5)
        
        Returns:
            AgentResponse containing image specifications and optionally image results
        """

        # Get section and slide data once
        section = self.session.memory.get_session_by_index(index=section_index)
        slide = self.session.memory.get_slide_by_index(
            section_index=section_index, slide_index=slide_index
        )

        # Prepare the prompt
        formatted_prompt = self._get_prompt(
            section=section, slide=slide, additional_data=additional_data
        )
        self.session.save_prompt(
            key=section.section_index, type="image", prompt=formatted_prompt
        )

        # Retry mechanism for LLM invocation and parsing
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempt {attempt + 1}/{max_retries} - Generating image specifications"
                )

                # Validate and enhance the prompt if necessary
                enhanced_prompt = self._validate_and_enhance_prompt(
                    formatted_prompt, attempt + 1
                )

                # Invoke LLM
                response = self.llm.invoke(enhanced_prompt)

                # Check if response is None or empty
                if response is None or (
                    hasattr(response, "content") and not response.content
                ):
                    raise ValueError(
                        f"LLM returned null or empty response on attempt {attempt + 1}"
                    )

                # Parse the response
                image_specs: ListImageSpec = self.output_parser.invoke(response)

                # If we get here, parsing was successful
                logger.info(
                    f"Successfully generated image specifications on attempt {attempt + 1}"
                )

                # Process images if search is requested
                results = []
                for image_spec in image_specs.images:
                    if search_images:
                        search_results = self._search_and_save_images(
                            image_spec.search_query,
                            num_images,
                            image_spec.description,
                            image_path=image_path,
                        )

                return AgentResponse(
                    status=AgentStatus.SUCCESS,
                    message=f"Successfully generated image specifications{' and found matching images' if search_images else ''} (attempt {attempt + 1})",
                    data={
                        "image_specs": image_specs.model_dump(),
                    },
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")

                # If this is not the last attempt, continue to retry
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in attempt {attempt + 2}...")
                    continue
                else:
                    # This was the last attempt, break out of the loop
                    break

        # If we get here, all retries failed
        logger.error(
            f"All {max_retries} attempts failed. Last error: {str(last_error)}"
        )

        return AgentResponse(
            status=AgentStatus.ERROR,
            message=f"Error in Enhanced Image Agent after {max_retries} attempts: {str(last_error)}",
            data={},
        )

    def _search_and_save_images(
        self,
        search_query: str,
        num_images: int,
        context_name: str,
        image_path: str,
        retry_attempts: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Search for images using available tools and save them to the session's image folder.

        Args:
            search_query: The search query to use
            num_images: Number of images to retrieve
            context_name: Name/context for the image (used for key generation)

        Returns:
            List of dictionaries containing image information including local paths
        """
        # Get the image search tool
        search_tool = self.get_tool("searxng_image_search")

        if not search_tool:
            logger.error("Image search tool not available")
            return []

        # Ensure the image folder exists
        image_folder = self._ensure_image_folder()
        if not image_folder:
            logger.error("Failed to create or access image folder")
            return []

        # Search for images
        self.session.output_message.add(
            f"Searching for images using query: '{search_query}'", level="info"
        )
        search_results = None
        for attempt in range(retry_attempts):
            search_results = search_tool._run(
                query=search_query, num_results=num_images
            )
            if (
                search_results
                and isinstance(search_results, list)
                and len(search_results) > 0
            ):
                break
            logger.warning(
                f"Attempt {attempt + 1}: No images found for query: '{search_query}'. Retrying..."
            )

        if not search_results or (
            isinstance(search_results, list) and len(search_results) == 0
        ):
            logger.warning(f"No images found for query: '{search_query}'")
            return []

        # Process and save each image
        processed_results = []
        for idx, result in enumerate(search_results):
            if "error" in result:
                logger.error(f"Error in search result: {result['error']}")
                continue

            try:
                # Download and save the image
                image_key, local_path = self._download_and_save_image(
                    img_url=result["img_src"],
                    context_name=context_name,
                    idx=idx,
                    save_path=image_path,
                )

                if not local_path:
                    continue

                # Add local path and key to the result
                result["local_path"] = local_path
                result["image_key"] = image_key
                processed_results.append(result)

            except Exception as e:
                logger.error(f"Failed to process image result: {str(e)}")

        # Log results
        logger.info(
            f"Successfully processed {len(processed_results)} images out of {len(search_results)} results"
        )
        self.session.output_message.add(
            f"Retrieved {len(processed_results)} images", level="info"
        )

        return processed_results

    def _ensure_image_folder(self) -> Optional[str]:
        """
        Ensure that the image folder exists in the session assets.

        Returns:
            Path to the image folder or None if it couldn't be created
        """
        try:
            # Get the image folder from session asset

            image_folder = self.session.get_assets_image_folder()

            # Create the folder if it doesn't exist
            os.makedirs(image_folder, exist_ok=True)

            return image_folder

        except Exception as e:
            logger.error(f"Failed to ensure image folder exists: {str(e)}")
            return None

    def _download_and_save_image(
        self, img_url: str, context_name: str, idx: int, save_path: str
    ) -> tuple[str, Optional[str]]:
        """
        Download an image and save it to the specified folder.

        Args:
            img_url: URL of the image to download
            image_folder: Folder to save the image to
            context_name: Name/context for the image (used for key generation)
            idx: Index of the image in the result set

        Returns:
            Tuple of (image_key, local_path) or (image_key, None) if download failed
        """
        try:
            # Generate a unique key for the image
            sanitized_context = "".join(c if c.isalnum() else "_" for c in context_name)
            image_key = f"{sanitized_context}_{idx}_{uuid.uuid4().hex[:8]}"

            # Determine file extension from URL or default to .jpg
            parsed_url = urlparse(img_url)
            path = parsed_url.path
            extension = os.path.splitext(path)[1].lower()

            # If no valid extension, default to .jpg
            if not extension or extension not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp",
                ".svg",
            ]:
                extension = ".jpg"

            # Create the local filename
            local_path = save_path

            # Download the image
            response = requests.get(img_url, stream=True, timeout=10)
            response.raise_for_status()

            # Save the image
            with open(local_path, "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

            logger.info(
                f"Successfully downloaded and saved image with key: {image_key}"
            )
            return image_key, local_path

        except Exception as e:
            logger.error(f"Failed to download image from {img_url}: {str(e)}")
            # Return the key even if download failed, so caller knows what happened
            return (
                image_key
                if "image_key" in locals()
                else f"failed_{uuid.uuid4().hex[:8]}"
            ), None

    def get_image_by_key(self, image_key: str) -> Optional[str]:
        """
        Get an image by its key.

        Args:
            image_key: Key of the image to retrieve

        Returns:
            Path to the image or None if not found
        """
        try:
            image_folder = self._ensure_image_folder()
            if not image_folder:
                return None

            # Look for files that start with the image key
            for filename in os.listdir(image_folder):
                if filename.startswith(image_key):
                    return os.path.join(image_folder, filename)

            logger.warning(f"No image found with key: {image_key}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving image by key: {str(e)}")
            return None

    def _validate_and_enhance_prompt(self, prompt: str, attempt: int) -> str:
        """
        Validate and potentially enhance the prompt for better LLM response reliability.

        Args:
            prompt: The original prompt
            attempt: Current retry attempt number

        Returns:
            Enhanced prompt string
        """
        # For later attempts, add additional instructions to ensure proper response
        if attempt > 1:
            enhancement = f"""

IMPORTANT: This is retry attempt {attempt}. Please ensure you provide a valid JSON response following the exact format specified. 
Do not return null, empty, or invalid responses. Always return a properly formatted JSON object with the required fields.
"""
            return prompt + enhancement

        return prompt

    def _is_valid_response(self, response) -> bool:
        """
        Check if the LLM response is valid and parseable.

        Args:
            response: The LLM response to validate

        Returns:
            True if response is valid, False otherwise
        """
        if response is None:
            return False

        # Check if response has content
        if hasattr(response, "content"):
            return response.content is not None and response.content.strip() != ""

        # For string responses
        if isinstance(response, str):
            return response.strip() != ""

        return True
