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
import fitz

def convert_pptx_to_pdf(pptx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    pptx_name = os.path.basename(pptx_path)
    # Thay bằng đường dẫn tuyệt đối
    pptx_path = os.path.abspath(pptx_path)
    output_dir = os.path.abspath(output_dir)
    command = [
        "docker",
        "run",
        "-v", f"{pptx_path}:/app/{pptx_name}",
        "-v", f"{output_dir}:/output",
        "libreoffice",
]		

    subprocess.run(command, check=True)
    pptx_name = pptx_path.split(".")[0]
    pdf_path = pptx_name + ".pdf"
    return pdf_path


def convert_pdf_to_img(pdf_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(pdf_path), "images")

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)  # page_number is 0-based
        pix = page.get_pixmap(dpi=200)  # you can increase dpi for better quality
    
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)
        relative_path = image_path.split("src", 1)[-1][8:]
        image_paths.append(relative_path)

    doc.close()
    return image_paths
def convert_pptx_to_img(pptx_path, output_dir=None):
    """
    Convert a PPTX file to images.
    
    Args:
        pptx_path (str): Path to the PPTX file.
        output_dir (str, optional): Directory to save the images. Defaults to None.
    
    Returns:
        list: List of paths to the generated image files.
    """
    pdf_path = convert_pptx_to_pdf(pptx_path, output_dir)
    return convert_pdf_to_img(pdf_path)

if __name__ == "__main__":
    # Example usage
    pptx_path = "slides/56bcd8b5-a30e-4dbe-9116-98ec778d4277/presentation.pptx"
    output_dir = "slides/56bcd8b5-a30e-4dbe-9116-98ec778d4277"
    response = convert_pptx_to_pdf(pptx_path, output_dir)
    print(convert_pdf_to_img(response))
