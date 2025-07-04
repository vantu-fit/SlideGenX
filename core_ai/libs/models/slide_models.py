"""
Data models for slides in the Tree of Thought slide generation system.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class Diagram(BaseModel):
    """Diagram specifications for a slide."""
    data: str = Field(..., description="Diagram data in a specific format")
    relations: str = Field(default_factory=list, description="Containt Object And Relationships between elements in the diagram")

class SlideContent(BaseModel):
    """Content for a specific slide."""
    
    # Title of the slide
    title: str
    
    # Main content of the slide
    content: Union[str, List[str]]
    
    # Optional speaker notes
    notes: Optional[str] = None
    
    # IDs or descriptions of images needed for the slide
    images_needed: List[str]  
    
    # IDs or descriptions of diagrams needed for the slide
    diagrams_needed: List[Diagram] 
            
    # Keywords for this slide
    keywords: List[str] 
    

class SectionContent(BaseModel):
    """Content for a section of the presentation."""
    slides: List[SlideContent] = Field(default_factory=list)

class CompletedSlide(BaseModel):
    """A completed slide with all elements integrated."""
    
    # Basic slide content
    slide_content: SlideContent
    
    # Image specifications included in the slide
    image_specs: Optional[Dict[str, Any]] = None
    
    # Diagram specifications included in the slide
    diagram_specs: Optional[Dict[str, Any]] = None
    
    # Data visualization specifications included in the slide
    data_viz_specs: Optional[Dict[str, Any]] = None
    
    # Style specifications applied to the slide
    style_specs: Optional[Dict[str, Any]] = None
    
    # The rendered or formatted slide content
    generated_slide: str
    
    # Layout information for the slide
    layout_info: Dict[str, Any] = Field(default_factory=dict)


class Presentation(BaseModel):
    """Complete presentation with all slides."""
    
    # Title of the presentation
    title: str
    
    # Description of the presentation
    description: Optional[str] = None
    
    # Outline of the presentation
    outline: Dict[str, Any]
    
    # Style information for the presentation
    style: Dict[str, Any]
    
    # All slides in the presentation
    slides: List[CompletedSlide]
    
    # Metadata for the presentation
    metadata: Dict[str, Any] = Field(default_factory=dict)