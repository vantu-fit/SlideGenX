import re

def is_valid_email(email: str) -> bool:
    """
    Validate the email format using a regular expression.
    
    Args:
        email (str): The email address to validate.
    
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None

import subprocess
import os

import aspose.slides as slides
import aspose.pydrawing as drawing

def pptx_to_png_aspose(pptx_path, output_dir):
    # Load presentation
    with slides.Presentation(pptx_path) as pres:
        # Lặp qua từng slide
        for i, slide in enumerate(pres.slides):
            # Tạo full scale image
            bmp = slide.get_thumbnail(1, 1)
            # Lưu thành PNG
            bmp.save(f"{output_dir}/slide_{i+1}.png", drawing.imaging.ImageFormat.png)

if __name__ == "__main__":
    # Example usage
    pptx_path = "../slides/7549431c-b522-47bd-b5b8-8d43df653a0f/presentation.pptx.pptx"
    output_dir = "../slides/7549431c-b522-47bd-b5b8-8d43df653a0f"
    pptx_to_png_aspose(pptx_path, output_dir)
    print(f"Converted {pptx_path} to PDF in {output_dir}")