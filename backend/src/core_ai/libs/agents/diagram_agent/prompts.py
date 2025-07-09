"""
Prompt templates for the Diagram Agent specifically tailored for Mermaid diagram generation with expanded diagram types.
"""

from langchain.prompts import PromptTemplate


# Base template for generating Mermaid diagram code
DIAGRAM_GENERATION_TEMPLATE = """
Create a Mermaid diagram to illustrate the following slide:
# Section:
{section}

# Slide:
{slide}

MERMAID DIAGRAM REQUIREMENTS:
VERY IMPORTANT: The content inside diagram MUST be in English, even if the slide content is in Vietnamese.
1. Select the MOST APPROPRIATE diagram type from the following options, with strong preference for non-flowchart options:
   - mindmap (for concept hierarchies and brainstorming)
   - timeline (for chronological sequences and historical events)
   - sequenceDiagram (for interactions and message exchanges)
   - classDiagram (for object structures and relationships)
   - stateDiagram (for state transitions and systems)
   - erDiagram (for database and entity relationships)
   - quadrantChart (for comparative positioning and analysis)
   - requirementDiagram (for system requirements and relationships)
   - sankey (for flow quantity visualization)
   - xyChart (for data correlation and trends)
   - blockDiagram (for system architecture and components)
   - c4Diagram (for software architecture visualization)
   - radar (for multi-variable data comparison)
   - journey (for user experience and customer journeys)
   - gantt (for project scheduling and timelines)
   - pie (for proportional data representation)
   - flowchart (only when other diagram types cannot effectively represent the concept)

2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list unless absolutely necessary for content representation. Choose a different diagram type to ensure visual variety throughout the presentation.

3. Provide complete, valid Mermaid code that follows proper syntax
4. Include a brief explanation of why you chose this specific diagram type
5. Keep the diagram focused, clear, and visually balanced (not too complex)
6. Avoid using Mermaid markdown syntax that is not officially supported

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

# Create the prompt templates
diagram_generation_prompt = PromptTemplate(
    input_variables=["section", "slide", "format_instructions"],
    template=DIAGRAM_GENERATION_TEMPLATE
)

DIAGRAM_ADDITION_TEMPLATE = """
Create a Mermaid diagram to illustrate the following slide:
# Section:
{section}

# Slide:
{slide}

# MERMAID DIAGRAM CODE:
{mermaid_code}

# IMPORTANT: 
{additional_data}

MERMAID DIAGRAM REQUIREMENTS:
1. Select the MOST APPROPRIATE diagram type from the following options, with strong preference for non-flowchart options:
   - mindmap (for concept hierarchies and brainstorming)
   - timeline (for chronological sequences and historical events)
   - sequenceDiagram (for interactions and message exchanges)
   - classDiagram (for object structures and relationships)
   - stateDiagram (for state transitions and systems)
   - erDiagram (for database and entity relationships)
   - quadrantChart (for comparative positioning and analysis)
   - requirementDiagram (for system requirements and relationships)
   - sankey (for flow quantity visualization)
   - xyChart (for data correlation and trends)
   - blockDiagram (for system architecture and components)
   - c4Diagram (for software architecture visualization)
   - radar (for multi-variable data comparison)
   - journey (for user experience and customer journeys)
   - gantt (for project scheduling and timelines)
   - pie (for proportional data representation)
   - flowchart (only when other diagram types cannot effectively represent the concept)

2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list unless absolutely necessary for content representation. Choose a different diagram type to ensure visual variety throughout the presentation.

3. Provide complete, valid Mermaid code that follows proper syntax
4. Include a brief explanation of why you chose this specific diagram type
5. Keep the diagram focused, clear, and visually balanced (not too complex)
6. Avoid using Mermaid markdown syntax that is not officially supported

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

# Create the prompt templates
diagram_addition_prompt = PromptTemplate(
    input_variables=["section", "slide","mermaid_code", "additional_data", "format_instructions"],
    template=DIAGRAM_ADDITION_TEMPLATE
)

DIAGRAM_ADVOID_TYPE_TEMPLATE = """
Create a Mermaid diagram to illustrate the following slide:
# Section:
{section}

# Slide:
{slide}

# IMPORTANT: Dont user the following diagram types:
{previously_used_diagram_types}

MERMAID DIAGRAM REQUIREMENTS:
1. Select the MOST APPROPRIATE diagram type from the following options, with strong preference for non-flowchart options:
   - mindmap (for concept hierarchies and brainstorming)
   - timeline (for chronological sequences and historical events)
   - sequenceDiagram (for interactions and message exchanges)
   - classDiagram (for object structures and relationships)
   - stateDiagram (for state transitions and systems)
   - erDiagram (for database and entity relationships)
   - quadrantChart (for comparative positioning and analysis)
   - requirementDiagram (for system requirements and relationships)
   - sankey (for flow quantity visualization)
   - xyChart (for data correlation and trends)
   - blockDiagram (for system architecture and components)
   - c4Diagram (for software architecture visualization)
   - radar (for multi-variable data comparison)
   - journey (for user experience and customer journeys)
   - gantt (for project scheduling and timelines)
   - pie (for proportional data representation)
   - flowchart (only when other diagram types cannot effectively represent the concept)

2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list unless absolutely necessary for content representation. Choose a different diagram type to ensure visual variety throughout the presentation.

3. Provide complete, valid Mermaid code that follows proper syntax
4. Include a brief explanation of why you chose this specific diagram type
5. Keep the diagram focused, clear, and visually balanced (not too complex)
6. Avoid using Mermaid markdown syntax that is not officially supported

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

# Create the prompt templates
diagram_advoid_type_prompt = PromptTemplate(
    input_variables=["section", "slide", "previously_used_diagram_types", "format_instructions"],
    template=DIAGRAM_ADVOID_TYPE_TEMPLATE
)



