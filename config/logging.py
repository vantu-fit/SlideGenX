"""
Logging configuration for the application.
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict
import uuid


class LoggingManager:
    """Manage logging configurations for different contexts."""
    
    _initialized = False
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def initialize_app_logging(cls, log_level: str = 'DEBUG') -> str:
        """Initialize application-level logging (for CLI mode)."""
        if cls._initialized:
            return ""
            
        # Setup basic console logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[logging.StreamHandler()],
            force=True
        )
        
        cls._initialized = True
        return "Console logging initialized"
    
    @classmethod
    def setup_session_logging(cls, 
                            session_id: str, 
                            mode: str = 'generator', 
                            log_level: str = 'DEBUG') -> str:
        """
        Setup logging for a specific session (CLI or API request).
        
        :param session_id: Unique session identifier
        :param mode: Application mode ('generator' or 'editor')
        :param log_level: Logging level
        :return: Log filename created
        """
        if mode == 'editor':
            log_dir = 'logs/slide_editor'
            prefix = 'se'
        else:
            log_dir = 'logs/slide_generator'
            prefix = 'sg'
        
        # Create logs directory
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Generate log filename with session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"{log_dir}/{prefix}_{timestamp}_{session_id[:8]}.log"
        
        # Create session-specific logger
        logger_name = f"session_{session_id}"
        session_logger = logging.getLogger(logger_name)
        
        # Clear existing handlers for this logger
        for handler in session_logger.handlers[:]:
            session_logger.removeHandler(handler)
        
        # Create file handler for this session
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - [%(session_id)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        
        session_logger.addHandler(file_handler)
        session_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Store logger reference
        cls._loggers[session_id] = session_logger
        
        # Log initialization
        session_logger.info(f"Session logging initialized for mode: {mode}", 
                          extra={'session_id': session_id})
        session_logger.info(f"Log file: {log_filename}", 
                          extra={'session_id': session_id})
        
        return log_filename
    
    @classmethod
    def get_session_logger(cls, session_id: str) -> logging.Logger:
        """Get logger for a specific session."""
        return cls._loggers.get(session_id, logging.getLogger())
    
    @classmethod
    def cleanup_session_logging(cls, session_id: str):
        """Cleanup logging resources for a session."""
        if session_id in cls._loggers:
            logger = cls._loggers[session_id]
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            del cls._loggers[session_id]


def setup_logging(log_level: str = 'DEBUG', mode: str = 'generator') -> str:
    """
    Legacy function for CLI compatibility.
    """
    session_id = str(uuid.uuid4())
    return LoggingManager.setup_session_logging(session_id, mode, log_level)


def get_logger(name: str, session_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    :param name: The name of the logger
    :param session_id: Optional session ID for session-specific logging
    :return: Logger instance
    """
    if session_id:
        session_logger = LoggingManager.get_session_logger(session_id)
        return session_logger.getChild(name)
    return logging.getLogger(name)