"""
Prompt templates for the Image Agent.
"""

from langchain.prompts import PromptTemplate


# Base template for generating image specifications
GENERAL_TEMPLATE = """
Suggest an appropriate image for a slide with the following details:

# SECTION:
{section}

# SLIDE:
{slide}

Provide a detailed description of an ideal image, including its style, size, placement on the slide,
and a specific search query that could be used to find this image.

{format_instructions}
"""

REFIT_TEMPLATE = """
Suggest an appropriate image for a slide with the following details:

# SECTION:
{section}

# SLIDE:
{slide}

# IMPORTTANT:
{additional_data}

Provide a detailed description of an ideal image, including its style, size, placement on the slide,
and a specific search query that could be used to find this image.

{format_instructions}
"""

# Create the prompt templates
general_prompt = PromptTemplate(
    input_variables=["section", "slide", "format_instructions"],
    template=GENERAL_TEMPLATE
)

refit_prompt = PromptTemplate(
    input_variables=["section", "slide", "additional_data", "format_instructions"],
    template=REFIT_TEMPLATE
)