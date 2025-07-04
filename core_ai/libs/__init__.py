"""
Tree of Thought Slide Generator package.

This package contains a system for generating presentation slides using 
a Tree of Thought architecture with multiple specialized agents.
"""

__version__ = "0.1.0"
__author__ = "AI Team"
__license__ = "MIT"

from libs.orchestration.orchestrator import TreeOfThoughtOrchestrator
from libs.core.session import Session
from libs.config import load_config, save_config, TreeOfThoughtConfig

__all__ = [
    'TreeOfThoughtOrchestrator',
    'Session',
    'load_config',
    'save_config',
    'TreeOfThoughtConfig'
]