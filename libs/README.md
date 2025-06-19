```bash
libs                                 # Root directory containing all application components
├── agents                           # Directory containing all agent implementations
│   ├── diagram_agent                # Specialized agent for creating diagrams and visualizations
│   │   ├── agent.py                 # Main implementation of the diagram agent with core functionality
│   │   ├── evaluation.py            # Functions to evaluate diagram quality and relevance
│   │   ├── __init__.py              # Package initialization file for diagram_agent module
│   │   ├── prompts.py               # Templates and prompts used for diagram generation
│   │   └── tools.py                 # Utility tools specific to diagram creation
│   ├── image_agent                  # Specialized agent for handling images in presentations
│   │   ├── agent.py                 # Main implementation of the image agent
│   │   ├── evaluation.py            # Functions to evaluate image quality and relevance
│   │   ├── __init__.py              # Package initialization file for image_agent module
│   │   ├── prompts.py               # Templates and prompts used for image selection/generation
│   │   └── tools.py                 # Utility tools specific to image processing
│   ├── outline_agent                # Agent responsible for creating presentation outlines
│   │   ├── agent.py                 # Main implementation of the outline agent
│   │   ├── evaluation.py            # Functions to evaluate outline quality and structure
│   │   ├── __init__.py              # Package initialization file for outline_agent module
│   │   ├── prompts.py               # Templates and prompts for outline generation
│   ├── slide_content_agent          # Agent that generates the content for individual slides
│   │   ├── agent.py                 # Main implementation of the slide content agent
│   │   ├── evaluation.py            # Functions to evaluate slide content quality
│   │   ├── __init__.py              # Package initialization file for slide_content_agent module
│   │   ├── prompts.py               # Templates and prompts for slide content generation
│   ├── slide_generator_agent        # Agent that assembles the final presentation
│   │   ├── agent.py                 # Main implementation of the slide generator agent
│   │   ├── create_presetation.py    # Functions to create the final PowerPoint presentation
│   │   ├── evaluation.py            # Functions to evaluate overall presentation quality
│   │   ├── __init__.py              # Package initialization file for slide_generator_agent module
│   │   ├── prompts.py               # Templates and prompts for slide generation
│   │   ├── schemas.py               # Data schemas defining slide structures
│   │   ├── slide_handler.py         # Handles slide creation and management
│   │   └── tools.py                 # Utility tools specific to slide generation
│   ├── tools.py                     # Common tools shared across different agents
│   └── utils.py                     # Utility functions for agent operations
├── config.py                        # Configuration settings for the application
├── core                             # Core system components
│   ├── agent_response.py            # Defines response structure for agents
│   ├── agent_status.py              # Manages agent status tracking
│   ├── base_agent.py                # Base class from which all agents inherit
│   ├── __init__.py                  # Package initialization file for core module
│   └── session.py                   # Manages session information and state
├── create_pptx.py                   # Functions to create PowerPoint presentations
├── __init__.py                      # Package initialization file for libs module
├── main.py                          # Entry point for the application
├── models                           # Data models used throughout the application
│   ├── outline_models.py            # Data models for presentation outlines
│   ├── slide_models.py              # Data models for slides and slide content
│   ├── style_models.py              # Data models for presentation styles
│   └── visualization_models.py      # Data models for visualizations and diagrams
├── orchestration                    # Handles coordination between agents
│   ├── orchestrator.py              # Orchestrates the workflow between different agents
├── README.md                        # Project documentation
├── run.py                           # Runner script for the presentation generator
└── utils                            # Utility modules for the application
    ├── file.py                      # Basic file operations
    ├── file_utils.py                # Advanced file utilities
    ├── __init__.py                  # Package initialization file for utils module
    ├── llm_utils.py                 # Utilities for working with language models
    ├── merge_pptx.py                # Tool to merge PowerPoint presentations (fixes broken PPTX files)
    ├── pptx2pdf.py                  # Converts PowerPoint presentations to PDF
    └── web.py                       # Web-related utilities
```
# Running the application:
python -m libs.main \
        --topic "$(cat topic.txt)" \            # Topic for presentation, read from topic.txt file
        --audience "Small and medium businesses" \ # Target audience
        --duration 20 \                          # Presentation duration in minutes
        --template 
        --template "libs/pptx_templates/modern.pptx" \ # Path to the PowerPoint templat
        --purpose "Education and persuasion" \   # Purpose of the presentation
        --output presentation.pptx              # Output filename
