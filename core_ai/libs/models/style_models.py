"""
Data models for styles in the Tree of Thought slide generation system.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SlideStyle(BaseModel):
    """Style specifications for slides."""
    
    # Color scheme (list of color hex codes)
    color_scheme: List[str]
    
    # Font family for text
    font_family: str
    
    # Font sizes for different text elements (title, body, etc.)
    font_sizes: Dict[str, int]
    
    # Background style (solid, gradient, image, etc.)
    background_style: str
    
    # Transition style between slides
    transitions: str
    
    # Optional theme name
    theme_name: Optional[str] = None
    
    # Optional accent color
    accent_color: Optional[str] = None
    
    # Text colors for different elements
    text_colors: Dict[str, str] = Field(default_factory=dict)
    
    # Spacing settings
    spacing: Dict[str, Any] = Field(default_factory=dict)
    
    # Alignment preferences
    alignment: Dict[str, str] = Field(default_factory=dict)
    
    # Boolean settings
    settings: Dict[str, bool] = Field(default_factory=dict)
    
    # Animation settings
    animations: Dict[str, Any] = Field(default_factory=dict)
    
    # Logo settings
    logo: Dict[str, Any] = Field(default_factory=dict)


class StyleTemplate(BaseModel):
    """A reusable style template."""
    
    # Template ID
    template_id: str
    
    # Template name
    name: str
    
    # Template description
    description: str
    
    # The actual style specifications
    style: SlideStyle
    
    # Tags for categorizing the template
    tags: List[str] = Field(default_factory=list)
    
    # Suitable use cases
    use_cases: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BrandGuidelines(BaseModel):
    """Brand guidelines for consistent styling."""
    
    # Company or brand name
    brand_name: str
    
    # Primary color
    primary_color: str
    
    # Secondary colors
    secondary_colors: List[str] = Field(default_factory=list)
    
    # Primary font
    primary_font: str
    
    # Secondary font
    secondary_font: Optional[str] = None
    
    # Logo information
    logo: Dict[str, Any] = Field(default_factory=dict)
    
    # Brand voice guidelines
    voice: Dict[str, str] = Field(default_factory=dict)
    
    # Do's and don'ts
    guidelines: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Additional brand assets
    assets: Dict[str, Any] = Field(default_factory=dict)