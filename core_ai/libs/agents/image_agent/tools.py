"""
Tool for searching images using searXNG API
"""

import logging
import requests
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

logger = logging.getLogger(__name__)

class ImageSearchInput(BaseModel):
    """Input for SearXNG Image Search Tool."""
    
    query: str = Field(
        ..., 
        description="The search query for finding relevant images"
    )
    num_results: int = Field(
        default=5, 
        description="Number of image results to return (default is 5)"
    )
    safe_search: int = Field(
        default=1, 
        description="Safe search level: 0=off, 1=moderate, 2=strict"
    )
    engines: Optional[str] = Field(
        default=None,
        description="Comma-separated list of specific search engines to use (e.g., 'google images,bing images')"
    )

class ImageResult(BaseModel):
    """Model for image search result."""
    
    title: str = Field(description="Title or description of the image")
    url: str = Field(description="URL to the page containing the image")
    img_src: str = Field(description="Direct URL to the image file")
    thumbnail: Optional[str] = Field(description="URL to thumbnail version of the image")
    source: str = Field(description="Source engine that provided this result")
    width: Optional[int] = Field(description="Width of the image if available")
    height: Optional[int] = Field(description="Height of the image if available")
    img_format: Optional[str] = Field(description="Format of the image if available")

class SearXNGImageSearchTool(BaseTool):
    """Tool that searches for images using searXNG."""
    
    name : str = "searxng_image_search"
    description : str = "Searches for images based on a query using searXNG. Useful for finding relevant images for presentations, blog posts, or any visual content needs."
    
    searxng_instance: str = "http://localhost:8080"
    
    def _run(
        self, 
        query: str,
        num_results: int = 1,
        safe_search: int = 1,
        engines: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run image search with searXNG.
        
        Args:
            query: The search query
            num_results: Number of results to return
            safe_search: Safe search level (0=off, 1=moderate, 2=strict)
            engines: Comma-separated list of specific search engines to use
            run_manager: Callback manager
            
        Returns:
            List of image search results
        """
        try:
            # Build search parameters
            search_url = f"{self.searxng_instance}/search"
            params = {
                'q': query,
                'categories': 'images',
                'format': 'json',
                'pageno': 1,
                'safesearch': safe_search,
            }
            
            # Add engines if specified
            if engines:
                params['engines'] = engines
                
            # Log the search attempt
            logger.info(f"Searching for images with query: '{query}'")
            
            # Make request to searXNG
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse results
            results = response.json()
            images = results.get('results', [])
            
            # Limit number of results
            limited_results = images[:num_results]
            
            # Format results for better readability
            formatted_results = []
            for img in limited_results:
                result = {
                    'title': img.get('title', 'No title'),
                    'url': img.get('url', ''),
                    'img_src': img.get('img_src', ''),
                    'thumbnail': img.get('thumbnail', img.get('img_src', '')),
                    'source': img.get('engine', 'Unknown'),
                }
                
                # Add optional fields if available
                if 'img_format' in img:
                    result['img_format'] = img['img_format']
                if 'width' in img and 'height' in img:
                    result['width'] = img['width']
                    result['height'] = img['height']
                    
                formatted_results.append(result)
            
            logger.info(f"Found {num_results} image results for query '{query}'")
            return formatted_results[:num_results]
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error searching images: {str(e)}"
            logger.error(error_msg)
            return [{"error": error_msg}]
        except Exception as e:
            error_msg = f"Unexpected error during image search: {str(e)}"
            logger.error(error_msg)
            return [{"error": error_msg}]
    
    async def _arun(
        self,
        query: str,
        num_results: int = 1,
        safe_search: int = 1,
        engines: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[Dict[str, Any]]:
        """Async implementation of the image search tool."""
        # This is a simple implementation that calls the sync version
        # For production, you might want to use aiohttp instead
        return self._run(
            query=query,
            num_results=num_results,
            safe_search=safe_search,
            engines=engines,
        )
    
    def _get_tool_input_schema(self) -> Type[BaseModel]:
        """Get the input schema for the tool."""
        return ImageSearchInput


# Factory function to create the tool with custom settings
def create_searxng_image_search_tool(
    searxng_instance: str = "http://localhost:8080"
) -> SearXNGImageSearchTool:
    """
    Create an instance of the SearXNG Image Search Tool with custom settings.
    
    Args:
        searxng_instance: URL of the searXNG instance
        
    Returns:
        Configured SearXNGImageSearchTool instance
    """
    return SearXNGImageSearchTool(searxng_instance=searxng_instance)