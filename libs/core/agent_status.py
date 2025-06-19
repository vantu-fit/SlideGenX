"""
Status codes for agent responses in the Tree of Thought slide generation system.
"""


class AgentStatus:
    """Status codes for agent responses."""
    
    # Success status
    SUCCESS = "success"
    
    # Error status
    ERROR = "error"
    
    # In progress status - for long running operations
    IN_PROGRESS = "in_progress"
    
    # Canceled status - for operations canceled by the user
    CANCELED = "canceled"
    
    # Timeout status - for operations that exceeded their time limit
    TIMEOUT = "timeout"