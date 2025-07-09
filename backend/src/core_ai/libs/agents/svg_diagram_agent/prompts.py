"""
Prompt templates for the SVG Diagram Agent specifically tailored for SVG diagram generation.
"""

from langchain.prompts import PromptTemplate

SVG_GENERATION_TEMPLATE = """  
Create an SVG diagram to illustrate the following slide:  
# Section:  
{section}  
  
# Slide:  
{slide}  


# IMPORTANT: Do not use the following diagram types:  
{previously_used_diagram_types}  
  
SVG DIAGRAM REQUIREMENTS:  
VERY IMPORTANT: The content inside diagram MUST be in English, even if the slide content is in Vietnamese.
1. Select the MOST APPROPRIATE diagram type, prioritizing SVG's data visualization strengths:  
   - bar (for data comparison with animated bars)  
   - line (for trends with smooth curves or markers)  
   - scatter (for data correlation with custom markers)  
   - gauge (for performance metrics with needle animation)  
   - donut (for proportional data with a central label)  
   - comparison (for side-by-side analysis with gradients or icons)  
   - radar (for multi-variable comparison with filled areas)  
   - sankey (for flow quantity visualization with gradient paths)  
   - network (for interconnected nodes with custom layouts)  
   - hierarchy (for organizational structures with styled nodes)  
   - relationship (for entity connections with styled edges)  
   - quadrant (for 2x2 matrices with custom styling)  
   - pie (for proportional data with dynamic segments)  
   - timeline (for chronological sequences with styled milestones)  
   - mindmap (for concept hierarchies with unique node designs)  
   - flowchart (for process flows with custom shapes or animations) 


2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list. Only reuse a type if no other type can represent the content effectively, and provide a specific justification based on the slide content.

3. Provide complete, valid SVG code that follows proper XML syntax, including:
   - A fixed size of 800x600px (suitable for 16:9 slides) unless the slide specifies otherwise.
   - Font-family Arial or Sans-serif, with font-size >= 14px for readability at 2m distance.
   - A maximum of 3-5 colors for visual consistency, using a simple palette (e.g., #007bff, #ff6b6b, #4ecdc4).
   - Optional subtle animations (e.g., hover effects, fade-in) only if specified in the slide content or additional_data.

4. Include a brief explanation of:
   - Why you chose this specific diagram type (e.g., how it aligns with the slide content).
   - Why other diagram types were not selected (especially if reusing a previously used type).

5. Keep the diagram focused, clear, and visually balanced:
   - Limit to 10-15 elements (nodes, edges, or shapes) to avoid clutter.
   - Ensure text is legible and elements are evenly spaced within the 800x600px canvas.

6. Ensure SVG is self-contained with no external dependencies (e.g., no external fonts or images).

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

svg_generation_prompt = PromptTemplate(
    input_variables=["section", "slide", "previously_used_diagram_types", "format_instructions"],
    template=SVG_GENERATION_TEMPLATE
)

SVG_ADDITION_TEMPLATE = """
Create an SVG diagram to illustrate the following slide:
# Section:
{section}

# Slide:
{slide}

# SVG CODE:
{svg_code}

# IMPORTANT: Do not use the following diagram types:  
{previously_used_diagram_types}

# IMPORTANT:
{additional_data}

SVG DIAGRAM REQUIREMENTS:
1. Select the MOST APPROPRIATE diagram type, prioritizing SVG's data visualization strengths:  
   - bar (for data comparison with animated bars)  
   - line (for trends with smooth curves or markers)  
   - scatter (for data correlation with custom markers)  
   - gauge (for performance metrics with needle animation)  
   - donut (for proportional data with a central label)  
   - comparison (for side-by-side analysis with gradients or icons)  
   - radar (for multi-variable comparison with filled areas)  
   - sankey (for flow quantity visualization with gradient paths)  
   - network (for interconnected nodes with custom layouts)  
   - hierarchy (for organizational structures with styled nodes)  
   - relationship (for entity connections with styled edges)  
   - quadrant (for 2x2 matrices with custom styling)  
   - pie (for proportional data with dynamic segments)  
   - timeline (for chronological sequences with styled milestones)  
   - mindmap (for concept hierarchies with unique node designs)  
   - flowchart (for process flows with custom shapes or animations)

2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list unless absolutely necessary for content representation. Choose a different diagram type to ensure visual variety.

3. Provide complete, valid SVG code that follows proper XML syntax
4. Include a brief explanation of why you chose this specific diagram type
5. Keep the diagram focused, clear, and visually balanced (not too complex)
6. Ensure SVG is self-contained with no external dependencies

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

svg_addition_prompt = PromptTemplate(  
    input_variables=["section", "slide", "svg_code", "previously_used_diagram_types", "additional_data", "format_instructions"],  
    template=SVG_ADDITION_TEMPLATE  
)

SVG_AVOID_TYPE_TEMPLATE = """
Create an SVG diagram to illustrate the following slide:
# Section:
{section}

# Slide:
{slide}

# IMPORTANT: Do not use the following diagram types:
{previously_used_diagram_types}

SVG DIAGRAM REQUIREMENTS:
1. Select the MOST APPROPRIATE diagram type, prioritizing SVG's data visualization strengths:  
   - bar (for data comparison with animated bars)  
   - line (for trends with smooth curves or markers)  
   - scatter (for data correlation with custom markers)  
   - gauge (for performance metrics with needle animation)  
   - donut (for proportional data with a central label)  
   - comparison (for side-by-side analysis with gradients or icons)  
   - radar (for multi-variable comparison with filled areas)  
   - sankey (for flow quantity visualization with gradient paths)  
   - network (for interconnected nodes with custom layouts)  
   - hierarchy (for organizational structures with styled nodes)  
   - relationship (for entity connections with styled edges)  
   - quadrant (for 2x2 matrices with custom styling)  
   - pie (for proportional data with dynamic segments)  
   - timeline (for chronological sequences with styled milestones)  
   - mindmap (for concept hierarchies with unique node designs)  
   - flowchart (for process flows with custom shapes or animations)

2. IMPORTANT: AVOID selecting any diagram type that appears in the PREVIOUSLY USED DIAGRAM TYPES list unless absolutely necessary for content representation. Choose a different diagram type to ensure visual variety.

3. Provide complete, valid SVG code that follows proper XML syntax
4. Include a brief explanation of why you chose this specific diagram type
5. Keep the diagram focused, clear, and visually balanced (not too complex)
6. Ensure SVG is self-contained with no external dependencies

IMPORTANT: Your response MUST be in the following format to be correctly processed:

{format_instructions}
"""

svg_avoid_type_prompt = PromptTemplate(
    input_variables=["section", "slide", "previously_used_diagram_types", "format_instructions"],
    template=SVG_AVOID_TYPE_TEMPLATE
)