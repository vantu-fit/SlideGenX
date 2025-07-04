from core_ai.libs.main import gen_slide
import os

class SlideService:
    """
    Service for generating slides.
    """

    def __init__(self):
        """
        Initialize the SlideService.
        """
        pass

    def get_template_path(self, template_name: str) -> str:
        """
        Get the path to the template based on the template name.

        Args:
            template_name (str): Name of the template.

        Returns:
            str: Path to the template.
        """
        return f"core_ai/pptx_templates/{template_name}.pptx"
    
    def list_templates(self) -> list:
        """
        List available templates.

        Returns:
            list: List of available template names.
        """
        templates_dir = "core_ai/pptx_templates"
        try:
            return [f[:-5] for f in os.listdir(templates_dir) if f.endswith('.pptx')]
        except FileNotFoundError:
            return []

    def generate_slide(self, title: str, content: str, duration: int, purpose: str, output_file_name: str, template: str = None):
        """
        Generate a slide with the given parameters.

        Args:
            title (str): Title of the slide.
            content (str): Content of the slide.
            duration (int): Duration for which the slide is valid.
            purpose (str): Purpose of the slide.
            output_path (str): Path to save the generated slide.
            template_path (str, optional): Path to the template to use. Defaults to None.

        Returns:
            bool: True if successful, False otherwise.
        """
        template_path = self.get_template_path(template) if template else self.get_template_path("Blank")
        output_path = f"slides/{output_file_name}.pptx"
        result = gen_slide(title, content, duration, purpose, output_path, template_path)
        return result
    
if __name__ == "__main__":
    # Example usage
    slide_service = SlideService()
    success = slide_service.generate_slide(
        title="Deep Learning",
        content="Deep learning is a subset of machine learning that uses neural networks with many layers.",
        duration=45,
        purpose="educate",
        output_file_name="deep_learning",
        template="FIT-HCMUS_template"
    )
    print("Slide generated successfully:", success)