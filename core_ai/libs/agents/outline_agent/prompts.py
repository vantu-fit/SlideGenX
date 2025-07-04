"""
Prompt templates for the Outline Agent with an emphasis on diagram creation and agenda/table of contents.
"""

from langchain_core.prompts.prompt import PromptTemplate


# Base template for generating presentation outlines
OUTLINE_GENERATION_TEMPLATE = """
Create a detailed, in-depth presentation outline for the topic: {topic}

Audience: {audience}  
Duration: {duration} minutes  
Purpose: {purpose}  

IMPORTANT: Structure the outline as follows:
- Title Slide (1 slide) 
- Agenda Slide (1 slide) 
- Chapter sections (each with >3 slide)
- Conclusion Slide (2 slide)
- Q&A Slide (2 slide)

Each section should include:
- Clear section title
- Description of purpose or focus
- Key points and subpoints
- Estimated number of slides (minimum 3 per section)

Diagram guidance:
- Only include diagrams if essential for understanding
- Specify diagram type and key elements (e.g., flowchart with A→B→C)
- Provide 1 simple Mermaid diagram for a critical concept
- Prioritize text-based explanation over visuals

IMPORTANT: Structure the outline as follows:
- Title Slide (1 slide) 
- Agenda Slide (1 slide)
- Chapter sections (each with >3 slide)
- Conclusion Slide (2 slide) 
- Q&A Slide (2 slide)

SECTION_TYPE: Thera are 5 section types: "title", "agenda", "chapter", "conclusion" , "qa" 

{format_instructions}
"""


# Template for generating presentation outlines with specific considerations
OUTLINE_GENERATION_WITH_CONTEXT_TEMPLATE = """
Create a detailed presentation outline for a presentation on {topic}.

Audience: {audience}
Duration: {duration} minutes
Purpose: {purpose}
Context/Industry: {context}
Brand Guidelines: {brand_guidelines}

The outline should align with the specified context and brand guidelines.
Include:
1. A compelling title slide (1 slide)
2. A dedicated agenda/table of contents section (1 slide) listing all major sections
3. Multiple content sections with clear descriptions and key points
4. A conclusion slide (1 slide)

Estimate the number of slides needed for each section and the presentation as a whole.

DIAGRAM REQUIREMENTS:
1. Create detailed diagram specifications for AT LEAST the title slide and conclusion slide
2. For each diagram, provide the diagram type (flowchart, sequence, class, state, ER, gantt, pie, etc.)
3. Include specific diagram elements, connections, and relationships to be visualized
4. Avoid suggesting static images - ALL visual elements should be diagram-based
5. Consider using additional diagrams for key concepts in content slides where appropriate
6. Provide basic Mermaid diagram code for at least one of the suggested diagrams

AGENDA/CONTENTS REQUIREMENTS:
1. The agenda slide must immediately follow the title slide
2. Create a SIMPLE text-based agenda listing the main sections - avoid complex visual elements
3. Only include a diagram in the agenda slide if ABSOLUTELY NECESSARY for understanding the presentation structure
4. If a diagram is necessary, keep it minimal and focused only on essential structural elements while respecting brand guidelines

Diagrams should effectively model and visualize the key concepts, relationships, or flow of information in the presentation.
Focus on creating a diagram-rich structure that will engage this specific audience and achieve the stated purpose.

{format_instructions}
"""

# Template for generating alternative outlines based on an existing one
OUTLINE_VARIATION_TEMPLATE = """
Create a different presentation outline approach for the following presentation details:

Topic: {topic}
Audience: {audience}
Number Slides: {duration} slides
Purpose: {purpose}

Original Outline:
{original_outline}

Create a new outline with a different approach, structure, or perspective. 
The new outline should still be appropriate for the audience and purpose, but offer a fresh take on the topic.
Include:
1. A compelling title slide (1 slide)
2. A dedicated agenda/table of contents section (1 slide) listing all major sections
3. Multiple content sections with clear descriptions and key points
4. A conclusion slide (1 slide)

Estimate the number of slides needed for each section and the presentation as a whole.

DIAGRAM REQUIREMENTS:
1. Create detailed diagram specifications for AT LEAST the title slide and conclusion slide
2. For each diagram, provide the diagram type (flowchart, sequence, class, state, ER, gantt, pie, etc.)
3. Include specific diagram elements, connections, and relationships to be visualized
4. Avoid suggesting static images - ALL visual elements should be diagram-based
5. Consider using additional diagrams for key concepts in content slides where appropriate
6. Provide basic Mermaid diagram code for at least one of the suggested diagrams

AGENDA/CONTENTS REQUIREMENTS:
1. The agenda slide must immediately follow the title slide
2. Create a SIMPLE text-based agenda listing the main sections - avoid complex visual elements
3. Only include a diagram in the agenda slide if ABSOLUTELY NECESSARY for understanding the presentation structure
4. If a diagram is necessary, keep it minimal and focused only on essential structural elements
5. Make this agenda approach different from the one in the original outline while maintaining simplicity

Diagrams should effectively model and visualize the key concepts, relationships, or flow of information in the presentation.
This new approach should be more diagram-focused than the original outline.

{format_instructions}
"""

CLASSIFY_LAYOUT_PROMPT = """
You are given a list of PowerPoint slide layouts from a template, each with its index, name, and the placeholders it contains (including type and label).

Here is the layout information:
{layout_information}

Your task is to classify the layouts into **6 groups** based on their appropriate use in a presentation report:

- "title": (1 slide) layouts used for the main title slide of the report
- "agenda": (1 slide) prefer vertiva title agenda layout, used for the agenda or table of contents
- "chapter_title": (1 slide) layouts used at the start of a new chapter/section (e.g. with "Horizontal Chaper" or "Vertical Chapter")
- "chapter": layouts used for presenting main content within a chapter (typically used 2–10 times) there are have type of data such as "title", "body", "object", "picture", "center_title", "slide_number", ...
- "conclusion": (2 slide) perfer vertical title conclusion layout, used for summarizing the report or providing final thoughts
- "qa": (2 slide) perfer horizontal title Q&A layout, used for the question and answer session

**Note**:
- A layout can belong to multiple groups if appropriate.
- Only return layout indexes (e.g. [1, 3, 5]), not names.
- Use placeholder names and types to help guide the classification (e.g. TITLE, SUBTITLE, BODY, OBJECT, PICTURE, CENTER_TITLE, SLIDE_NUMBER, etc.)

Return your answer in JSON format with the following structure:

{{
  "title": [...],
  "agenda": [ ... ],
  "chapter_title": [ ... ],
  "chapter": [ ... ],
  "conclusion": [ ... ],
  "qa": [ ... ]
}}
IMPORTTANT: Every type must have at least 3 layout in the list.

{format_instructions}
"""


# Create the prompt templates
outline_prompt = PromptTemplate(
    input_variables=["topic", "audience", "duration", "purpose", "format_instructions"],
    template=OUTLINE_GENERATION_TEMPLATE
)

outline_with_context_prompt = PromptTemplate(
    input_variables=["topic", "audience", "duration", "purpose", "context", "brand_guidelines", "format_instructions"],
    template=OUTLINE_GENERATION_WITH_CONTEXT_TEMPLATE
)

outline_variation_prompt = PromptTemplate(
    input_variables=["topic", "audience", "duration", "purpose", "original_outline", "format_instructions"],
    template=OUTLINE_VARIATION_TEMPLATE
)

classify_layout_prompt = PromptTemplate(
    input_variables=["layout_infomation", "format_instructions"],
    template=CLASSIFY_LAYOUT_PROMPT
)