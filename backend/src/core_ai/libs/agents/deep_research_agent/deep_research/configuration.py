from dataclasses import dataclass, fields
from langchain_core.runnables import RunnableConfig
import os
from typing import Any

@dataclass(kw_only=True)
class Configuration:

    provider: str = "google"
    model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    max_queries: int = 3
    search_depth: int = 2
    num_reflections: int = 1
    section_delay_seconds: int = 2
    max_sections: int = 3
    
    @classmethod
    def from_runnable_config(
        cls,
        config: RunnableConfig
    ) -> "Configuration":
        
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name, f.default))
            for f in fields(cls)
            if f.init
        }

        return cls(**values)