"""
Data models for presentation outlines in the Tree of Thought slide generation system.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class OutlineSection(BaseModel):
    """A section in the presentation outline."""
    
    # Title of the section
    title: str = Field(..., description="Title of the section")
    
    # Description of the section content
    description: str = Field(..., description="Description of the section content")
    
    # Key points to cover in this section
    key_points: List[str] = Field(..., description="Key points to cover in this section")
    
    # Estimated number of slides needed for this section
    estimated_slides: int = Field(..., description="Estimated number of slides needed for this section")

    # Index of the section in the outline
    section_index: int = Field(..., description="Index of the section in the outline")

    section_type : str =  Field(..., description="title, agenda, chapter, conclustion, q&a")


class PresentationOutline(BaseModel):
    """Complete presentation outline."""
    
    # Title of the presentation
    title: str  = Field(..., description="Title of the presentation")
    
    # Sections in the presentation
    sections: List[OutlineSection] = Field(..., description="Sections in the presentation")
    
    # Total number of slides in the presentation
    total_slides: int = Field(..., description="Total number of slides in the presentation")
    
    # Optional presentation description
    description: Optional[str] = Field(None, description="Description of the presentation")
    