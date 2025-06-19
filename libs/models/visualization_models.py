"""
Data models for visualizations in the Tree of Thought slide generation system.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class ImageSpec(BaseModel):
    """Specification for images to search."""
    # Detailed description of the image
    description: str
    # Search query to find this image
    search_query: str

class ListImageSpec(BaseModel):
    """Specification for a list of images."""
    # List of image specifications
    images: List[ImageSpec] = Field(default_factory=list)


class DiagramComponent(BaseModel):
    """A component in a diagram."""
    
    # Component ID
    id: str
    
    # Component type (e.g., "node", "box", "circle")
    type: str
    
    # Component label or text
    label: str
    
    # Optional position information
    position: Optional[Dict[str, Any]] = None
    
    # Optional style information
    style: Optional[Dict[str, Any]] = None
    
    # Optional properties
    properties: Dict[str, Any] = Field(default_factory=dict)


class DiagramConnection(BaseModel):
    """A connection between components in a diagram."""
    
    # Connection ID
    id: str
    
    # Source component ID
    source: str
    
    # Target component ID
    target: str
    
    # Optional label for the connection
    label: Optional[str] = None
    
    # Optional style information
    style: Optional[Dict[str, Any]] = None
    
    # Connection type (e.g., "arrow", "line", "dashed")
    type: Optional[str] = None
    
    # Optional properties
    properties: Dict[str, Any] = Field(default_factory=dict)


"""
Pydantic models for visualizations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DiagramSpec(BaseModel):
    """Specification for diagrams to create."""
    
    diagram_type: str = Field(
        ..., 
        description="The type of diagram to create (e.g., 'mindmap', 'sequenceDiagram', 'erDiagram', etc.)"
    )
    
    title: str = Field(
        ..., 
        description="A descriptive title for the diagram"
    )
    
    mermaid_code: str = Field(
        ..., 
        description="The Mermaid code for the diagram (without the triple backticks and without the mermaid keyword)"
    )
    

class DataPoint(BaseModel):
    """A single data point for visualization."""
    
    # X-axis value or label
    x: Any
    
    # Y-axis value
    y: Any
    
    # Optional category or series
    category: Optional[str] = None
    
    # Optional size (for bubble charts)
    size: Optional[float] = None
    
    # Optional color
    color: Optional[str] = None
    
    # Optional additional data
    data: Dict[str, Any] = Field(default_factory=dict)


class DataVisualizationSpec(BaseModel):
    """Specification for data visualizations."""
    
    # Type of chart (e.g., "bar", "line", "pie", "scatter")
    chart_type: str
    
    # Title of the chart
    title: str
    
    # Data structure for the visualization
    data_structure: Dict[str, Any]
    
    # X-axis label or field name
    x_axis: Optional[str] = None
    
    # Y-axis label or field name
    y_axis: Optional[str] = None
    
    # Colors for different series or categories
    colors: List[str] = Field(default_factory=list)
    
    # Optional subtitle
    subtitle: Optional[str] = None
    
    # Optional legend settings
    legend: Optional[Dict[str, Any]] = None
    
    # Optional axes settings
    axes: Optional[Dict[str, Any]] = None
    
    # Optional annotations
    annotations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Optional chart settings
    settings: Dict[str, Any] = Field(default_factory=dict)