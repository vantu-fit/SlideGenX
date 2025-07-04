"""
Utility functions for working with language models.
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_openai_llm(model_info: Dict[str, Any]):
    """
    Get an OpenAI language model.
    
    Args:
        model_info: Configuration for the model
        
    Returns:
        OpenAI language model instance
    """
    try:
        from langchain.llms import OpenAI
        
        # Get API key from model_info or environment variable
        api_key = model_info.get("api_key") or os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please provide it in model_info or set OPENAI_API_KEY environment variable.")
        
        # Get model parameters
        model_name = model_info.get("model_name", "gpt-4")
        temperature = model_info.get("temperature", 0.7)
        max_tokens = model_info.get("max_tokens", 2000)
        
        # Additional parameters
        additional_params = model_info.get("additional_params", {})
        
        # Create and return the model
        return OpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **additional_params
        )
    except ImportError:
        logger.error("Failed to import OpenAI LLM. Make sure langchain is installed.")
        raise


def get_anthropic_llm(model_info: Dict[str, Any]):
    """
    Get an Anthropic language model.
    
    Args:
        model_info: Configuration for the model
        
    Returns:
        Anthropic language model instance
    """
    try:
        from langchain.llms import Anthropic
        
        # Get API key from model_info or environment variable
        api_key = model_info.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("Anthropic API key not found. Please provide it in model_info or set ANTHROPIC_API_KEY environment variable.")
        
        # Get model parameters
        model_name = model_info.get("model_name", "claude-2")
        temperature = model_info.get("temperature", 0.7)
        max_tokens = model_info.get("max_tokens", 2000)
        
        # Additional parameters
        additional_params = model_info.get("additional_params", {})
        
        # Create and return the model
        return Anthropic(
            anthropic_api_key=api_key,
            model=model_name,
            temperature=temperature,
            max_tokens_to_sample=max_tokens,
            **additional_params
        )
    except ImportError:
        logger.error("Failed to import Anthropic LLM. Make sure langchain is installed.")
        raise


def get_huggingface_llm(model_info: Dict[str, Any]):
    """
    Get a HuggingFace language model.
    
    Args:
        model_info: Configuration for the model
        
    Returns:
        HuggingFace language model instance
    """
    try:
        from langchain.llms import HuggingFaceHub
        
        # Get API key from model_info or environment variable
        api_key = model_info.get("api_key") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        
        if not api_key:
            raise ValueError("HuggingFace API token not found. Please provide it in model_info or set HUGGINGFACEHUB_API_TOKEN environment variable.")
        
        # Get model parameters
        model_name = model_info.get("model_name", "google/flan-t5-xxl")
        temperature = model_info.get("temperature", 0.7)
        max_length = model_info.get("max_tokens", 2000)
        
        # Additional parameters
        additional_params = model_info.get("additional_params", {})
        
        # Create and return the model
        return HuggingFaceHub(
            huggingfacehub_api_token=api_key,
            repo_id=model_name,
            model_kwargs={
                "temperature": temperature,
                "max_length": max_length,
                **additional_params
            }
        )
    except ImportError:
        logger.error("Failed to import HuggingFace LLM. Make sure langchain is installed.")
        raise


def get_llm(model_info: Dict[str, Any], model_index: int = 0):
    """
    Get a language model based on provider.
    
    Args:
        model_info: Dictionary of model configurations
        model_index: Index of the model to use
        
    Returns:
        Language model instance
    """
    # If model_info is a list, get the specified model by index
    if isinstance(model_info, list):
        if model_index >= len(model_info):
            logger.warning(f"Model index {model_index} out of range. Using model at index 0.")
            model_index = 0
        
        model_info = model_info[model_index]
    
    # Get provider from model_info
    provider = model_info.get("provider", "openai").lower()
    
    # Get the appropriate model based on provider
    if provider == "openai":
        return get_openai_llm(model_info)
    elif provider == "anthropic":
        return get_anthropic_llm(model_info)
    elif provider == "huggingface":
        return get_huggingface_llm(model_info)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def format_prompt_template(template: str, **kwargs) -> str:
    """
    Format a prompt template with the provided values.
    
    Args:
        template: The prompt template
        **kwargs: Values to fill in the template
        
    Returns:
        Formatted prompt
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing key in prompt template: {e}")
        raise


def count_tokens(text: str, model_name: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text.
    
    Args:
        text: The text to count tokens for
        model_name: The model name to use for tokenization
        
    Returns:
        Number of tokens
    """
    try:
        import tiktoken
        
        # Get the encoding for the model
        enc = tiktoken.encoding_for_model(model_name)
        
        # Count tokens
        return len(enc.encode(text))
    except ImportError:
        logger.warning("tiktoken not installed. Estimating tokens based on words.")
        # Rough estimation: 1 token ≈ 0.75 words
        return int(len(text.split()) / 0.75)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback estimation
        return int(len(text) / 4)