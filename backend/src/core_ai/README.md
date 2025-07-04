# SlideGenX - AI-Powered Presentation Generator

## Prerequisites

### 1. Install Required Tools
To generate diagrams, ensure the following tools are installed globally:

#### Install `svgexport`
```bash
npm install -g svgexport
```

#### Install `@mermaid-js/mermaid-cli`
```bash
npm install -g @mermaid-js/mermaid-cli
```

These tools are required for generating diagrams in the presentation slides.

### 2. Run SearXNG
```bash
docker compose up -d
```

---

## Usage

### Generate slide

```
python -m libs.main \
			--topic "$(cat topic.txt)" \
			--audience "Small and medium businesses" \
			--duration 20 \
			--purpose "Education and persuasion" \
			--template pptx_templates/Geometric.pptx \
			--output presentation.pptx
```

### Edit slide

```
python -m libs.main \
    --edit \
    --session-path "memory.json" \
    --section-index 4 \
    --slide-index 2 \
    --edit-prompt "Show information about AI in medical-healthcare, not about marketing and sales" \
    --merge-output-path "updated_presentation.pptx"
```

---

# CORE-AI DOCUMENTATION

## Core Functions

### 1.Generate Slide

**Trigger Function:** `TreeOfThoughtOrchestrator.generate_presentation()`  
**Location:** `libs/orchestration/orchestrator.py`

#### Input Parameters:

- `topic` (str): Presentation topic (can be read from topic.txt file)
- `audience` (str): Target audience (e.g., "Small and medium businesses")
- `duration` (int): Presentation duration in minutes
- `purpose` (str): Presentation purpose (e.g., "Education and persuasion")
- `output_path` (str): Output file path (.pptx)
- `template_path` (str): PowerPoint template file path (e.g., "pptx_templates/Geometric.pptx")
- `parallel` (bool): Enable parallel processing or sequential (default: True)
- `pdf` (bool): Generate PDF output or not (default: True)

#### Response Format:

**SUCCESS Response:**

```json
{
    "status": "success",
    "message": "Successfully generated presentation with X slides",
    "data": {
        "outline": {
            "title": "Presentation Title",
            "sections": [...]
        },
        "slides": [...],
        "metadata": {
            "topic": "...",
            "audience": "...",
            "duration": 20,
            "purpose": "...",
            "total_slides": 10,
            "parallel_processing": true
        }
    }
}
```

**ERROR Response:**

```json
{
  "status": "error",
  "message": "Error description",
  "data": {}
}
```

**Possible Error Messages:**

- `"Failed to generate presentation outline"`
- `"Failed to generate any valid slides"`
- `"Failed to merge presentation slides: [details]"`
- `"Failed to generate presentation: [details]"`

---

### 2. Edit Slide
**Trigger Function:** `SlideEditOrchestrator.edit_slide()`  
**Location:** `libs/orchestration/slide_edit_orchestrator.py`

#### Input Parameters:
- `session_path` (str): Path to session file (e.g., "memory.json")
- `section_index` (int): Index of section containing the slide (0-based)
- `slide_index` (int): Index of slide within the section (0-based)
- `edit_prompt` (str): User's edit instructions
- `merge_output_path` (str, optional): Path to save merged output after editing

#### Response Format:

**SUCCESS Response:**
```json
{
    "status": "success",
    "message": "Slide edited successfully",
    "data": {
        "section_index": 4,
        "slide_index": 2,
        "new_content": {
            "title": "Updated Title",
            "content": "Updated Content",
            "notes": "Updated Notes",
            "keywords": ["keyword1", "keyword2"]
        },
        "slide_path": "path/to/generated/slide.pptx",
        "merged_presentation_path": "updated_presentation.pptx"
    }
}
```

**ERROR Response:**
```json
{
    "status": "error",
    "message": "Error description",
    "data": {}
}
```

**Possible Error Messages:**
- `"Invalid section or slide index"`
- `"Slide or section not found"`
- `"Failed to generate new slide content"`
- `"Failed to generate new slide"`
- `"Error editing slide: [details]"`

---

## Notes
- Ensure `svgexport` and `@mermaid-js/mermaid-cli` are installed globally for diagram generation.
- Session files (`memory.json`) are automatically generated during slide generation.
- Section and slide indices are 0-based.
- Template files should be placed in `pptx_templates/` directory.
- Output files will be saved to the specified paths.
