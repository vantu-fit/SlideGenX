"""
Prompt templates for the Slide Generator Agent.
"""
from langchain.prompts import PromptTemplate

CHOOSE_LAYOUT_PROMPT = """

You are an expert presentation designer selecting the best PowerPoint slide layout.

### Input:
- Section Information: {section}
- Slide Content: {slides}
- Available Layouts: {layout_information}

### Task:
Choose the most appropriate layout for each slide based on:
1. Content type & amount (title, bullet points, paragraphs)
2. Media type & aspect ratio:
   - Wide (ratio > 1.3)
   - Square (0.8 < ratio < 1.3)
   - Tall (ratio < 0.8)
3. Slide purpose: 
   - First slide = title slide (use TITLE/CENTER_TITLE layouts)
   - Section start = section title
   - Content-heavy = BODY layout
   - Media = PICTURE layout
4. Text & media matching:
   - Text = TITLE, BODY, OBJECT layouts
   - Image = PICTURE layout
   - Diagram = PICTURE layout


### Output:
Return a list of layout indices for each slide in order.

{format_instructions}
"""

CHOOSE_LAYOUT_CHAPTER_PROMPT = """
CHOOSE_LAYOUT_PROMPT:

You are an expert presentation designer selecting the best PowerPoint slide layout.

### Input:
- Section Information: {section}
- Slide Content: {slides}
- Chapter Slide Information: {chapter_slide}
- Slide Layouts: {layout_information}

### Task:
Choose the most appropriate layout for each slide based on:
1. Content type & amount (title, bullet points, paragraphs)
2. Media type & aspect ratio:
   - Wide (ratio > 1.3)
   - Square (0.8 < ratio < 1.3)
   - Tall (ratio < 0.8)
3. Slide purpose: 
   - First slide = title slide (use TITLE/CENTER_TITLE layouts)
   - Section start = section title
   - Content-heavy = BODY layout
   - Media = PICTURE layout
4. Text & media matching:
   - Text = TITLE, BODY, OBJECT layouts
   - Image = PICTURE layout
   - Diagram = PICTURE layout


### Output:
Return a list of layout indices for each slide in order.

{format_instructions}
"""

TRY_OTHER_LAYOUT_PROMPT = """
You are an expert presentation designer who selects the most suitable PowerPoint slide layout.

The previous layout choice(s) didn't work well for this slide. Select a different, better option.

## SECTION INFORMATION:
{section}

## SLIDE CONTENT:
{slides}

## AVAILABLE MASTER SLIDE LAYOUTS:
{layout_information}

## PREVIOUSLY TRIED LAYOUTS (AVOID THESE):
{previous_layouts}

Your task is to analyze the slide content and choose a DIFFERENT, MORE APPROPRIATE layout number.

Consider these factors in your decision:
1. Slide content type and amount (title only, bullet points, paragraphs, etc.)
2. Media content type (prioritize diagrams over images when both are present)
3. Media aspect ratio (width/height):
   - Wide/landscape: ratio > 1.3
   - Square: ratio between 0.8 and 1.3
   - Tall/portrait: ratio < 0.8

4. Slide purpose and position in the presentation:
   - First slide of first section = title slide (look for layout with TITLE or CENTER_TITLE placeholders)
   - Section start = section title slide
   - Content-heavy slide = layout with BODY placeholder
   - Slide with media = layout with PICTURE, CHART, or DIAGRAM placeholders based on media type

5. Matching placeholder types to content:
   - For text content: use layouts with TITLE, BODY, or OBJECT placeholders
   - For images: use layouts with PICTURE placeholders
   - For diagrams/charts: use layouts with CHART or DIAGRAM placeholders
   - When both images and diagrams are present, prioritize layouts with DIAGRAM/CHART placeholders

Select a layout that can accommodate ALL the content without overcrowding.

Return ONLY the numeric layout index that best matches this slide content. Just the number.

{format_instructions}
"""


FIT_CONTENT_PROMPT = """
You are an expert presentation designer specializing in fitting content to PowerPoint slide placeholders.

Section content: 
{section}

## SLIDE CONTENT AND LAYOUTS:
{inputs}

## TASK:
Map slide content (title, text, picture) from the provided section and slide data to the appropriate placeholders in each slide's layout. Create a mapping where each placeholder index is assigned the appropriate content.

### Rules:
1. **Prioritize content placement**:
   - Place slide title in the most prominent placeholder first.
   - Place key content (e.g., key points, diagrams) in prominent placeholders.

3. **Handle all placeholders**:
   - Map content to all relevant placeholders in the slide's layout, excluding SLIDE_NUMBER (13) unless specified.
   - Assign empty string (`""`) or array (`[]`) to placeholders with no suitable content.
   - if placeholder for image then value is path to picture ()

Output a `slides` array, where each element has a `mappings` object with placeholder indices (as strings) mapped to a string (e.g., title, diagram path) or an array of strings (e.g., bullet points).
You can generate more information to fill all placeholder from content i provied


### Example:
For a slide with layout:
- Placeholder index: 2, name: Title 1
- Placeholder index: 1, name: Text Placeholder
- Content: Title "Introduction", bullet points ["Point 1", "Point 2"]

Output:
```json
{sample}
```

{format_instructions}
"""

CLASSIFY_LAYOUT_PROMPT = """
You are given a list of PowerPoint slide layouts from a template, each with its index, name, and the placeholders it contains (including type and label).

Here is the layout information:
{layout_infomation}

Your task is to classify the layouts into **6 groups** based on their appropriate use in a presentation report:

- "title": layouts used for the main title slide of the report
- "agenda": layouts used for listing agenda or overview of contents
- "chapter_title": layouts used at the start of a new chapter/section (e.g. with "Chapter_title" or "Chapter_titleonly")
- "chapter": layouts used for presenting main content within a chapter (typically used 2–10 times)
- "conclusion": layouts used to summarize chapter or presentation content
- "Q&A": layouts used for displaying questions or for discussion

**Note**:
- A layout can belong to multiple groups if appropriate.
- Only return layout indexes (e.g. [1, 3, 5]), not names.
- Use placeholder names and types to help guide the classification (e.g. TITLE, BODY, OBJECT, PICTURE, CENTER_TITLE, SLIDE_NUMBER, etc.)

Return your answer in JSON format with the following structure:

{{
  "title": [...],
  "agenda": [ ... ],
  "chapter_title": [ ... ],
  "chapter": [ ... ],
  "conclusion": [ ... ],
  "Q&A": [ ... ]
}}



{format_instructions}
"""

# Create the prompt templates
choose_layout_prompt = PromptTemplate(
    input_variables=["section", "slides", "layout_information", "format_instructions"],
    template=CHOOSE_LAYOUT_PROMPT
)

try_other_layout_prompt = PromptTemplate(
    input_variables=["section", "slides", "layout_information", "previous_layouts", "format_instructions"],
    template=TRY_OTHER_LAYOUT_PROMPT
)


fit_content_prompt = PromptTemplate(
    input_variables=["section", "inputs", "sample", "format_instructions"],
    template=FIT_CONTENT_PROMPT
)

classify_layout_prompt = PromptTemplate(
    input_variables=["layout_infomation", "format_instructions"],
    template=CLASSIFY_LAYOUT_PROMPT
)

choose_layout_chapter_prompt = PromptTemplate(
    input_variables=["section", "slides", "chapter_slide", "layout_information", "format_instructions"],
    template=CHOOSE_LAYOUT_CHAPTER_PROMPT
)