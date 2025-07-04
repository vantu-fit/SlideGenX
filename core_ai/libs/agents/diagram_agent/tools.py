"""
Implementation of the MermaidTool for converting Mermaid diagram code to PNG images.
"""

import logging
import os
import subprocess
import tempfile
import shutil
import io
from pathlib import Path
from typing import Dict, Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MermaidToolInput(BaseModel):
    """Input for the MermaidTool."""
    mermaid_code: str = Field(..., description="The Mermaid diagram code as string")
    output_path: str = Field(..., description="Path where the output PNG file will be saved")
    theme: str = Field(default="default", description="Theme to use for rendering (default, dark, forest, neutral)")


class MermaidTool(BaseTool):
    """Tool for converting Mermaid diagrams to PNG images."""
    
    name : str = "mermaid_to_png"
    description : str  = "Converts Mermaid diagram code to a PNG image file"
    args_schema: Type[BaseModel] = MermaidToolInput
    
    def _run(self, mermaid_code: str, output_path: str, theme: str = "default") -> str:
        """
        Run the tool to convert Mermaid diagram code to PNG.
        
        Args:
            mermaid_code: The Mermaid diagram code as string
            output_path: Path where the output PNG file will be saved
            theme: Theme to use for rendering (default, dark, forest, neutral)
            
        Returns:
            str: A message indicating success or failure
        """
        # Use direct path to mmdc
        mmdc_path = "C:\\Program Files\\nodejs\\mmdc.CMD"
        if not os.path.exists(mmdc_path):
            # Try to find it if direct path doesn't work
            mmdc_path = shutil.which("mmdc")
            if not mmdc_path:
                error_msg = "mmdc executable not found. Make sure @mermaid-js/mermaid-cli is installed globally."
                logger.error(error_msg)
                return f"Error: {error_msg}"
        
        temp_file_path = None
        try:
            # Create a temporary file - use binary mode to avoid encoding issues
            fd, temp_file_path = tempfile.mkstemp(suffix='.mmd')
            os.close(fd)
            
            # Write content as ASCII-only
            simplified_code = ''.join(char if ord(char) < 128 else '_' for char in mermaid_code)
            with open(temp_file_path, 'w', encoding='ascii', errors='ignore') as temp_file:
                temp_file.write(simplified_code)
            
            # Debug log the content written to file
            logger.info(f"Content written to temp file: {simplified_code}")
            
            # Make sure output directory exists
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Run mmdc command with shell=True for Windows compatibility
            command = f'"{mmdc_path}" -i "{temp_file_path}" -o "{output_path}" -t {theme}'
            logger.info(f"Executing command: {command}")
            
            # Use shell=True for Windows command compatibility
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, command, output=stdout, stderr=stderr
                )
            
            success_msg = f"Successfully converted Mermaid diagram to {output_path}"
            logger.info(success_msg)
            logger.info(f"Command output: {stdout}")
            return success_msg
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Error converting Mermaid diagram: Command '{command}' returned non-zero exit status {e.returncode}."
            if e.stdout:
                error_msg += f"\nCommand output: {e.stdout}"
            if e.stderr:
                error_msg += f"\nCommand error: {e.stderr}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
    
    async def _arun(self, mermaid_code: str, output_path: str, theme: str = "default") -> str:
        """Async version of _run method."""
        return self._run(mermaid_code=mermaid_code, output_path=output_path, theme=theme)
    
    def get_tool_input_schema(self) -> Type[BaseModel]:
        """Get the input schema for this tool."""
        return self.args_schema
    
    def to_llm_format(self) -> Dict[str, Any]:
        """Convert the tool to a format suitable for the LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "args_schema": self.args_schema.schema()
        }


def create_diagram_mermaid_tool() -> MermaidTool:
    """Factory function to create a MermaidTool instance."""
    return MermaidTool()

if __name__ == "__main__":
    # Example usage
    tool = create_diagram_mermaid_tool()
    mermaid_code = """sequenceDiagram
    participant User
    participant System
    participant AI

    User->>System: Provide Template PPTX + Prompt
    System->>System: Extract Master Slide
    System->>AI: Process with AI Agent
    AI->>AI: Tree of Thought Analysis
    AI->>System: Generate Slides
    System->>User: Return generated slides
    User->>User: Review and evaluate
    
    alt Acceptable
        User->>User: Accept slides
    else Needs revision
        User->>System: Request modifications
        System->>AI: Return to processing
    end"""
    output_path = "output/diagram.png"
    result = tool._run(mermaid_code=mermaid_code, output_path=output_path)
    print(result)