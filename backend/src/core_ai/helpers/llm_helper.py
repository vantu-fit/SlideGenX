"""
Helper functions to access LLMs.
"""
import logging
import re
import sys
import urllib3
from typing import Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from langchain_core.language_models import BaseLLM, BaseChatModel


sys.path.append('..')

from core_ai.config.global_config import GlobalConfig


LLM_PROVIDER_MODEL_REGEX = re.compile(r'\[(.*?)\](.*)')
OLLAMA_MODEL_REGEX = re.compile(r'[a-zA-Z0-9._:-]+$')
# 94 characters long, only containing alphanumeric characters, hyphens, and underscores
API_KEY_REGEX = re.compile(r'^[a-zA-Z0-9_-]{6,94}$')
REQUEST_TIMEOUT = 35


logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.ERROR)

retries = Retry(
    total=5,
    backoff_factor=0.25,
    # backoff_jitter=0.3,
    status_forcelist=[502, 503, 504],
    allowed_methods={'POST'},
)
adapter = HTTPAdapter(max_retries=retries)
http_session = requests.Session()
http_session.mount('https://', adapter)
http_session.mount('http://', adapter)

def get_langchain_llm(
        provider: str,
        model: str,
        max_new_tokens: int,
        api_key: str = '',
        base_url: str = '',
) -> Union[BaseLLM, BaseChatModel, None]:
    """
    Get an LLM based on the provider and model specified.

    :param provider: The LLM provider. Valid values are `hf` for Hugging Face.
    :param model: The name of the LLM.
    :param max_new_tokens: The maximum number of tokens to generate.
    :param api_key: API key or access token to use.
    :param azure_endpoint_url: Azure OpenAI endpoint URL.
    :param azure_deployment_name: Azure OpenAI deployment name.
    :param azure_api_version: Azure OpenAI API version.
    :return: An instance of the LLM or Chat model; `None` in case of any error.
    """

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        logger.debug('Getting LLM via OpenAI API: %s', model)

        # The `model` parameter is not used here; `azure_deployment` points to the desired name
        return ChatOpenAI(
            model=model,
            base_url=base_url,
            temperature=GlobalConfig.LLM_MODEL_TEMPERATURE,
            max_tokens=max_new_tokens,
            timeout=None,
            max_retries=1,
            api_key=api_key,
        )

    if provider == "ollama":
        from langchain_ollama.llms import OllamaLLM

        logger.debug('Getting LLM via Ollama: %s', model)
        return OllamaLLM(
            model=model,
            temperature=GlobalConfig.LLM_MODEL_TEMPERATURE,
            num_predict=max_new_tokens,
            format='json',
        )
    
    if provider == "deepseek":
        from langchain_deepseek.chat_models import ChatDeepSeek
        logger.debug('Getting LLM via DeepSeek: %s', model)
        return ChatDeepSeek(
            model=model,
            temperature=GlobalConfig.LLM_MODEL_TEMPERATURE,
            max_tokens=max_new_tokens,
        )
    if provider == "gemini":
        # logger.debug('Getting LLM via Gemini: %s', model)
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            max_tokens=max_new_tokens,
            timeout=None,
            max_retries=2,
            api_key=api_key
        )

    return None

