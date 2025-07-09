"""
Prompt templates for the Slide Content Agent with balanced visual element constraints.
"""
from langchain_core.prompts.prompt import PromptTemplate


# Base template for generating multiple slide content from a section
SECTION_SLIDES_CONTENT_TEMPLATE = """
You are an expert presentation content designer and can use Vietnamese as fluent as a native speaker. Your task is to create slides for the specified section of a presentation in Vietnamese.

IMPORTANT: "Have many image or diagram"


{data}

**LANGUAGE**: Vietnamese

**SLIDE DESIGN INSTRUCTIONS**:
- Generate **{estimated_slides} slides** for this section, covering all key ideas clearly.
- Each slide must include:
  - `title`: Slide title
  - `content`: Bullet points or main content
  - `speaker_notes`: Notes for the presenter

IMPORTANT: 'title' MUST be long enough to be meaningful, but not too long to fit in a single line. Ideally, it should be 4-6 words.

**SLIDE FORMATTING RULES**:
- For section types:
  - `"title"`, `"agenda"`, `"conclusion"`, `"Q&A"` → Follow standard title/content flow.
  - `"chapter"` → First slide of the section MUST (VERY IMPORTANT):
    - Use the section title as `title`
    - Use the {chapter_number} as `content`
    - No speaker notes on this first chapter slide

VERY IMPORTTANT: If {section_type} == "chapter", the first slide of the section MUST use the {chapter_number} as `content` field.

IMPORTANT
**EXAMPLE – First Slide of a Section with section_type == "chapter"**:
```json
  "title": "Customer Retention Strategy",
  "content": "01",
```

VISUAL DESIGN RULES:
- Use 1–3 visuals per section, as needed for clarity.
- Only ONE visual per slide: either a diagram or an image — never both.
- Always prefer diagrams over images when both are appropriate (important).

IMPORTANT
DIAGRAM:
- data: contains the numerical or factual information used to create the diagram
- relations: contains the workflow or relationships between object

IMAGE: query to search image

IMPORTANT: "Have many image or diagram"
IMPORTANT: "Have many image or diagram"

VERY IMPORTTANT: If {section_type} == "chapter", the first slide of the section MUST use the {chapter_number} as `content` field.
VERY IMPORTTANT: If {section_type} == "chapter", the first slide of the section MUST use the {chapter_number} as `content` field.

**OUTPUT FORMAT**:
{format_instructions}
"""

# Create the prompt templates
section_slides_content_prompt = PromptTemplate(
    template=SECTION_SLIDES_CONTENT_TEMPLATE,
    input_variables=["topic", "presentation_title", "audience", "purpose", "data", "estimated_slides", 
                     "format_instructions", "chapter_number", "section_type"],
)