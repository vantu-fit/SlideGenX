import subprocess
import os
import logging
import argparse
import shutil
import platform


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SlideGenerateAgent")


def convert_to_pdf(ppt_path: str, output_path: str) -> None:
    """
    Convert a PowerPoint presentation to PDF using LibreOffice.
    Args:
        ppt_path: Path to the PowerPoint file
        output_path: Path to save the PDF
    """
    try:
        # Get the output directory, use '.' (current directory) if empty
        output_dir = os.path.dirname(output_path)
        if not output_dir:
            output_dir = "."

        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                ppt_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Check the stderr output for potential issues and log them
        if result.stderr:
            stderr_output = result.stderr.decode("utf-8").strip()
            if stderr_output:  # Only log if there's actual content
                logger.warning(f"Conversion warning: {stderr_output}")

        # Rename the generated file to the desired output_path
        base_name = os.path.basename(ppt_path)
        pdf_name = os.path.splitext(base_name)[0] + ".pdf"
        generated_pdf_path = os.path.join(output_dir, pdf_name)
        if generated_pdf_path != output_path:
            os.rename(generated_pdf_path, output_path)
        logger.info(f"PDF saved to {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error converting to PDF: {e.stderr.decode('utf-8').strip() if e.stderr else str(e)}"
        )
        raise
    except Exception as e:
        logger.error(f"Unknown error during PDF conversion: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PowerPoint presentation to PDF using LibreOffice"
    )
    parser.add_argument("--input", required=True, help="Path to the PowerPoint file (.pptx)")
    parser.add_argument("--output", required=True, help="Path to save the PDF file")

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        exit(1)

    # Check if input file has correct extension
    if not args.input.lower().endswith((".ppt", ".pptx")):
        logger.error(f"Input file must be a PowerPoint file (.ppt or .pptx)")
        exit(1)

    # Ensure output file has .pdf extension
    if not args.output.lower().endswith(".pdf"):
        args.output += ".pdf"

    try:
        convert_to_pdf(args.input, args.output)
        print(f"Successfully converted {args.input} to {args.output}")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        exit(1)
