from PIL import Image
import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core_ai.helpers.llm_helper import get_langchain_llm

def get_llm(llm_info, model):
    return get_langchain_llm(
        provider=llm_info["provider"],
        model=model,
        max_new_tokens=llm_info["max_new_tokens"],
        api_key=llm_info["api_key"],
        base_url=llm_info["base_url"]
    )



def filter_slide_info(slide_data, base_dir="."):
    """
    Filters necessary information for slide creation and gets actual image dimensions
    
    Args:
        slide_data (list): List of slide data dictionaries
        base_dir (str): Base directory where image files are stored
        
    Returns:
        list: List of filtered slide information dictionaries
    """
    filtered_slides = []
    
    for slide in slide_data:
        filtered_slide = {
            "title": slide.get("title", ""),
            "content": slide.get("content", []),
            "section_index": slide.get("section_index", 0),
            "slide_index": slide.get("slide_index", 0),
            "diagrams": [],
            "images": []
        }

        if slide.get("diagram") and not isinstance(slide["diagram"], dict):
            slide["diagram"] = slide["diagram"].model_dump()

        if slide.get("image") and not isinstance(slide["image"], dict):
            slide["image"] = slide["image"].model_dump()

        

        
        # Process diagrams if available
        if slide.get("diagram") and slide["diagram"].get("status") == "success":
            diagram_data = slide["diagram"]["data"]
            diagram_path = diagram_data.get("diagram_path", "")
            full_diagram_path = os.path.join(base_dir, diagram_path)
            
            # Default values in case file can't be read
            width, height = 800, 600
            ratio = width / height
            
            # Try to get actual image dimensions
            try:
                if os.path.exists(full_diagram_path):
                    with Image.open(full_diagram_path) as img:
                        width, height = img.size
                        ratio = width / height
            except Exception as e:
                print(f"Error getting diagram dimensions for {diagram_path}: {e}")
            
            diagram_info = {
                "title": diagram_data.get("title", ""),
                "diagram_path": diagram_path,
                "width": width,
                "height": height,
                "ratio": ratio,
                "description": slide.get("diagrams_needed", [""])[0] if slide.get("diagrams_needed") else ""
            }
            filtered_slide["diagrams"].append(diagram_info)
        
        # Process images if available
        if slide.get("image") and slide["image"].get("status") == "success":
            image_specs = slide["image"]["data"]["image_specs"]
            for i, spec in enumerate(image_specs):
                for result in spec.get("image_results", []):
                    image_path = result.get("local_path", "")
                    full_image_path = os.path.join(base_dir, image_path)
                    
                    # Default values in case file can't be read
                    width, height = 800, 600
                    ratio = width / height
                    
                    # Try to get actual image dimensions
                    try:
                        if os.path.exists(full_image_path):
                            with Image.open(full_image_path) as img:
                                width, height = img.size
                                ratio = width / height
                    except Exception as e:
                        print(f"Error getting image dimensions for {image_path}: {e}")
                    
                    image_info = {
                        "title": result.get("title", ""),
                        "image_path": image_path,
                        "width": width,
                        "height": height,
                        "ratio": ratio,
                        "description": spec.get("description", "")
                    }
                    filtered_slide["images"].append(image_info)
        
        filtered_slides.append(filtered_slide)
    
    return filtered_slides
