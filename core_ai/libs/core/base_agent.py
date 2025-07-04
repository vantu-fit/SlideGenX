"""
Base agent class for the Tree of Thought slide generation system.
All other agents should inherit from this class.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .agent_status import AgentStatus
from .agent_response import AgentResponse
from .session import Session, OutputMessage
import config.global_config as gcfg
from pydantic import BaseModel
# from libs.utils.llm_utils import get_llm
from libs.agents.utils import get_llm


logger = logging.getLogger(__name__)

class BaseAgentConfig(BaseModel):
    llm_index : int = gcfg.GlobalConfig.DEFAULT_MODEL_INDEX

class BaseAgent(ABC):
    """Interface for all agents. All agents should inherit from this class."""

    agent_name: str = "base_agent"
    description: str = "Base agent description"
    parameters: dict = {}

    def __init__(self, session: Session, **kwargs):
        self.session: Session = session
        self.output_message: OutputMessage = self.session.output_message        
        # Get LLM
        
        cfg = kwargs.get("cfg", None)   
        if not cfg:
            cfg = BaseAgentConfig()  

        if cfg and hasattr(cfg, "llm_index"):
            llm_info = gcfg.GlobalConfig.VALID_MODELS[cfg.llm_index]
            self.llm = get_llm(llm_info, cfg.llm_index)
        else:
            self.llm = None

    # def get_parameters(self):
    #     """Return the automatically inferred parameters for the function using the docstring of the function."""
    #     from openai_function_calling import FunctionInferrer
    #     function_inferrer = FunctionInferrer.infer_from_function_reference(self.run)
    #     function_json = function_inferrer.to_json_schema()
    #     parameters = function_json.get("parameters")
    #     if not parameters:
    #         raise Exception(
    #             "Failed to infer parameters, please define JSON instead of using this automated util."
    #         )
    #     return parameters

    def to_llm_format(self):
        """Convert the agent to LLM tool format."""
        return {
            "name": self.agent_name,
            "description": self.description,
            # "parameters": self.parameters,
        }

    @property
    def name(self):
        return self.agent_name

    @property
    def agent_description(self):
        return self.description

    def safe_call(self, *args, **kwargs):
        try:
            return self.run(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {self.agent_name} agent: {e}")
            return AgentResponse(status=AgentStatus.ERROR, message=str(e))

    @abstractmethod
    def run(self, *args, **kwargs) -> AgentResponse:
        """
        Main execution method for the agent.
        Must be implemented by all agent subclasses.
        
        Returns:
            AgentResponse: The response from the agent
        """
        pass