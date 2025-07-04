"""
A set of configurations used by the app.
"""
import logging
from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class GlobalConfig:
    """
    A data class holding the configurations.
    """
    VALID_MODELS = {
        'gpt-4o': {
            'provider': 'openai',
            'description': 'faster, detailed',
            'max_new_tokens': 4096,
            'paid': True,
            'api_key': os.getenv('OPENAI_API_KEY'),
            'base_url': os.getenv('OPENAI_API_BASE_URL')
        },
        # 'gemini-2.0-flash': {
        #     'provider': 'openai',
        #     'description': 'fast, detailed',
        #     'max_new_tokens': 4096,
        #     'paid': True,
        #     'api_key': os.getenv('OPENAI_API_KEY'),
        #     'base_url': os.getenv('OPENAI_API_BASE_URL')
        # },
        'llama3.1:latest': {
            'provider': 'ollama',
            'description': 'detailed, slower',
            'max_new_tokens': 4096,
            'paid': False,
            'api_key': None,
            'base_url': None
        },
        'deepseek-r1:latest': {
            'provider': 'ollama',
            'description': 'shorter, faster',
            'max_new_tokens': 4096,
            'paid': False,
            'api_key': None,
            'base_url': None
        },
        'deepseek-chat': {
            'provider': 'deepseek',
            'description': 'shorter, faster',
            'max_new_tokens': 4096,
            'paid': False,
            'api_key': os.getenv('DEEPSEEK_API_KEY'),
            'base_url': None
        },
        'gemini-2.0-flash': {
            'provider': 'gemini',
            'description': 'shorter, faster',
            'max_new_tokens': 4096,
            'paid': False,
            'api_key': os.getenv('GEMINI_API_KEY'),
            'base_url': None
        },
    }
    
    DEFAULT_MODEL_INDEX = 'gemini-2.0-flash'
    PLANNER_MODEL_INDEX = 'gpt-4o'
    GENERATOR_MODEL_INDEX = 'gpt-4o'
    SUMMARIZER_MODEL_INDEX = 'gpt-4o'
    SLIDEGEN_MODEL_INDEX = 'gpt-4o'

    # SEARXNG_ENDPOINT = "http://hc-c-008c2.hc.apac.bosch.com:8084/"
    SEARXNG_ENDPOINT = "http://localhost:8080/"
    
    LLM_MODEL_TEMPERATURE = 0.2
    LLM_MODEL_MIN_OUTPUT_LENGTH = 100
    LLM_MODEL_MAX_INPUT_LENGTH = 400  # characters
    MAX_PAGE_COUNT = 50

    LOG_LEVEL = 'DEBUG'
    COUNT_TOKENS = False
    APP_STRINGS_FILE = 'strings.json'
    PRELOAD_DATA_FILE = 'examples/example_02.json'
    SLIDES_TEMPLATE_FILE = 'langchain_templates/template_combined.txt'
    INITIAL_PROMPT_TEMPLATE = 'langchain_templates/chat_prompts/initial_template_v4_two_cols_img.txt'
    REFINEMENT_PROMPT_TEMPLATE = 'langchain_templates/chat_prompts/refinement_template_v4_two_cols_img.txt'

    LLM_PROGRESS_MAX = 90
    ICONS_DIR = 'icons/png128/'
    TINY_BERT_MODEL = 'gaunernst/bert-mini-uncased'
    EMBEDDINGS_FILE_NAME = 'file_embeddings/embeddings.npy'
    ICONS_FILE_NAME = 'file_embeddings/icons.npy'

    PPTX_TEMPLATE_FILES = {
        'Basic': {
            'file': 'pptx_templates/Blank.pptx',
            'caption': 'A good start 🟧'
        },
        'Ion Boardroom': {
            'file': 'pptx_templates/Ion_Boardroom.pptx',
            'caption': 'Make some bold decisions 🟥'
        },
        'Minimalist Sales Pitch': {
            'file': 'pptx_templates/Minimalist_sales_pitch.pptx',
            'caption': 'In high contrast ⬛'
        },
        'Urban Monochrome': {
            'file': 'pptx_templates/Urban_monochrome.pptx',
            'caption': 'Marvel in a monochrome dream ⬜'
        },
        'Bosch Weekly Report': {
            'file': 'pptx_templates/Bosch-WeeklyReport.pptx',
            'caption': 'Bosch Weekly Report'
        },

    }

    # This is a long text, so not incorporated as a string in `strings.json`
    CHAT_USAGE_INSTRUCTIONS = (
        'Briefly describe your topic of presentation in the textbox provided below. For example:\n'
        '- Make a slide deck on AI.'
        '\n\n'
        'Subsequently, you can add follow-up instructions, e.g.:\n'
        '- Can you add a slide on GPUs?'
        '\n\n'
        ' You can also ask it to refine any particular slide, e.g.:\n'
        '- Make the slide with title \'Examples of AI\' a bit more descriptive.'
        '\n\n'
        'Finally, click on the download button at the bottom to download the slide deck.'
        ' See this [demo video](https://youtu.be/QvAKzNKtk9k) for a brief walkthrough.\n\n'
        'Remember, the conversational interface is meant to (and will) update yor *initial*/'
        '*previous* slide deck. If you want to create a new slide deck on a different topic,'
        ' start a new chat session by reloading this page.'
        '\n\nSlideDeck AI can algo generate a presentation based on a PDF file. You can upload'
        ' a PDF file using the chat widget. Only a single file and up to max 50 pages will be'
        ' considered. For PDF-based slide deck generation, LLMs with large context windows, such'
        ' as Gemini, GPT, and Mistral-Nemo, are recommended. Note: images from the PDF files will'
        ' not be used.'
        '\n\nAlso, note that the uploaded file might disappear from the page after click.'
        ' You do not need to upload the same file again to continue'
        ' the interaction and refining—the contents of the PDF file will be retained in the'
        ' same interactive session.'
        '\n\nCurrently, paid or *free-to-use* LLMs from five different providers are supported.'
        ' A [summary of the supported LLMs]('
        'https://github.com/barun-saha/slide-deck-ai/blob/main/README.md#summary-of-the-llms)'
        ' is available for reference. SlideDeck AI does **NOT** store your API keys.'
        '\n\nSlideDeck AI does not have access to the Web, apart for searching for images relevant'
        ' to the slides. Photos are added probabilistically; transparency needs to be changed'
        ' manually, if required.\n\n'
        '[SlideDeck AI](https://github.com/barun-saha/slide-deck-ai) is an Open-Source project,'
        ' released under the'
        ' [MIT license](https://github.com/barun-saha/slide-deck-ai?tab=MIT-1-ov-file#readme).'
        '\n\n---\n\n'
        '© Copyright 2023-2025 Barun Saha.\n\n'
    )


logging.basicConfig(
    level=GlobalConfig.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_max_output_tokens(llm_name: str) -> int:
    """
    Get the max output tokens value configured for an LLM. Return a default value if not configured.

    :param llm_name: The name of the LLM.
    :return: Max output tokens or a default count.
    """

    try:
        return GlobalConfig.VALID_MODELS[llm_name]['max_new_tokens']
    except KeyError:
        return 2048
