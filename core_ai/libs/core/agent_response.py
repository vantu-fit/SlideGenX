"""
Response model for agents in the Tree of Thought slide generation system.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from .agent_status import AgentStatus


class AgentResponse(BaseModel):
    """Data model for responses from agents."""
    
    # Status of the agent's operation (success, error, etc.)
    status: str = AgentStatus.SUCCESS
    
    # A human-readable message about the operation
    message: str = ""
    
    # The actual data returned by the agent
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional metadata about the response
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional debug information - not included in production
    debug_info: Optional[Dict[str, Any]] = None
    
    def is_success(self) -> bool:
        """Check if the response indicates a successful operation."""
        return self.status == AgentStatus.SUCCESS
    
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return self.status == AgentStatus.ERROR
    
    def is_in_progress(self) -> bool:
        """Check if the operation is still in progress."""
        return self.status == AgentStatus.IN_PROGRESS