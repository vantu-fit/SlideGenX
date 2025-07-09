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

def convert_pptx_to_pdf(pptx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    command = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        pptx_path
    ]

    subprocess.run(command, check=True)
    pptx_name = pptx_path.split(".")[0]
    pdf_path = pptx_name + ".pdf"
    return pdf_path

def convert_pdf_to_img(pdf_path, output_dir = None):
    import pdf2image
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path) + "/images"
    print(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    print(pdf_path)
    # return
    images = pdf2image.convert_from_path(pdf_path, dpi=200, output_folder=os.path.dirname(pdf_path), fmt='png')
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i + 1}.png")
        image.save(image_path, 'PNG')
        image_paths.append(os.path.abspath(image_path))
    # remove the image in images folder
    for image in os.listdir(os.path.dirname(pdf_path)):
        if image.endswith('.png'):
            os.remove(os.path.join(os.path.dirname(pdf_path), image))
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
    pptx_path = "slides/40c6b22e-d668-4a7f-9846-5039f30753dc/deep_learning.pptx"
    output_dir = "slides/40c6b22e-d668-4a7f-9846-5039f30753dc"
    response = convert_pptx_to_pdf(pptx_path, output_dir)
    print(convert_pdf_to_img(response))