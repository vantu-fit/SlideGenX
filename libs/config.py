"""
Configuration settings for the Tree of Thought slide generation system.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for language models."""
    
    # Provider ("openai", "anthropic", "local", etc.)
    provider: str = "openai"
    
    # Model name
    # model_name: str = "gpt-4"
    
    # API key (should be set via environment variable in production)
    api_key: Optional[str] = None
    
    # Temperature (0.0 to 1.0)
    temperature: float = 0.7
    
    # Maximum tokens to generate
    max_tokens: int = 10000
    
    # Additional parameters
    additional_params: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Base configuration for agents."""
    
    # LLM index to use
    llm_index: str =  "gemini-2.0-flash"
    
    # Whether to use caching
    use_cache: bool = True
    
    # Number of retries on failure
    max_retries: int = 2
    
    # Timeout in seconds
    timeout: int = 60


class OutlineAgentConfig(AgentConfig):
    """Configuration for outline agents."""
    
    # Minimum number of sections
    min_sections: int = 3
    
    # Maximum number of sections
    max_sections: int = 7


class SlideContentAgentConfig(AgentConfig):
    """Configuration for slide content agents."""
    
    # Maximum content length
    max_content_length: int = 10000
    
    # Whether to include speaker notes
    include_speaker_notes: bool = True


class ImageAgentConfig(AgentConfig):
    """Configuration for image agents."""
    
    # List of preferred image styles
    preferred_styles: List[str] = Field(default_factory=lambda: ["professional", "modern", "clean"])
    
    # Image API to use
    image_api: str = "pexels"


class DiagramAgentConfig(AgentConfig):
    """Configuration for diagram agents."""
    
    # List of preferred diagram types
    preferred_diagram_types: List[str] = Field(default_factory=lambda: ["flowchart", "mindmap", "sequence"])
    
    # Whether to include descriptions
    include_descriptions: bool = True

class SVGDiagramAgentConfig(AgentConfig):
    """Configuration for SVG diagram agents."""
    
    preferred_svg_types: List[str] = Field(default_factory=lambda: ["bar", "line", "pie"])
    include_animation: bool = False
    

class DataVisualizationAgentConfig(AgentConfig):
    """Configuration for data visualization agents."""
    
    # List of preferred chart types
    preferred_chart_types: List[str] = Field(default_factory=lambda: ["bar", "line", "pie", "scatter"])
    
    # Default color scheme
    default_color_scheme: List[str] = Field(default_factory=lambda: ["#4285F4", "#34A853", "#FBBC05", "#EA4335"])


class StyleAgentConfig(AgentConfig):
    """Configuration for style agents."""
    
    # List of brand colors (if applicable)
    brand_colors: List[str] = Field(default_factory=list)
    
    # Preferred font families
    preferred_fonts: List[str] = Field(default_factory=lambda: ["Arial", "Helvetica", "Roboto"])


class SlideGeneratorAgentConfig(AgentConfig):
    """Configuration for slide generator agents."""
    
    # Output format
    output_format: str = "pptx"
    
    # Default template
    default_template: str = "modern"


class EvaluationConfig(BaseModel):
    """Configuration for evaluation."""
    
    # Whether to use LLM for evaluation
    use_llm_for_evaluation: bool = True
    
    # LLM index to use for evaluation
    evaluation_llm_index: str =  "gemini-2.0-flash"
    
    # Criteria weights
    criteria_weights: Dict[str, Dict[str, float]] = Field(default_factory=dict)


class TreeOfThoughtConfig(BaseModel):
    """Main configuration for the Tree of Thought system."""
    
    # Number of agents to use per task
    num_agents_per_task: int = 1
    
    # Maximum number of iterations
    max_iterations: int = 3
    
    # Whether to enable parallel processing
    enable_parallel: bool = True
    
    # Maximum number of parallel workers
    max_workers: int = 3
    
    # LLM configurations
    llm_configs: List[LLMConfig] = Field(default_factory=lambda: [LLMConfig()])
    
    # Agent configurations
    outline_agent_config: OutlineAgentConfig = Field(default_factory=OutlineAgentConfig)
    slide_content_agent_config: SlideContentAgentConfig = Field(default_factory=SlideContentAgentConfig)
    image_agent_config: ImageAgentConfig = Field(default_factory=ImageAgentConfig)
    diagram_agent_config: DiagramAgentConfig = Field(default_factory=DiagramAgentConfig)
    data_viz_agent_config: DataVisualizationAgentConfig = Field(default_factory=DataVisualizationAgentConfig)
    style_agent_config: StyleAgentConfig = Field(default_factory=StyleAgentConfig)
    slide_generator_agent_config: SlideGeneratorAgentConfig = Field(default_factory=SlideGeneratorAgentConfig)
    
    # Evaluation configuration
    evaluation_config: EvaluationConfig = Field(default_factory=EvaluationConfig)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


# Create default config
default_config = TreeOfThoughtConfig()


def load_config(config_path: Optional[str] = None) -> TreeOfThoughtConfig:
    """
    Load configuration from a file or use default.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Loaded configuration
    """
    if config_path:
        try:
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return TreeOfThoughtConfig(**config_data)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            print("Using default configuration")
    
    return default_config


def save_config(config: TreeOfThoughtConfig, config_path: str) -> bool:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration to save
        config_path: Path where to save the config
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import json
        with open(config_path, 'w') as f:
            json.dump(config.dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")
        return False