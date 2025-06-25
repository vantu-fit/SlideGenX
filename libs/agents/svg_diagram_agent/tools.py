"""
Implementation of the SVGExportTool for converting SVG diagram code to PNG images using svgexport CLI.
"""

import shutil
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SVGExportToolInput(BaseModel):
    """Input for the SVGExportTool."""
    svg_code: str = Field(..., description="The SVG diagram code as string")
    output_path: str = Field(..., description="Path where the output PNG file will be saved")

class SVGExportTool(BaseTool):
    """Tool for converting SVG diagrams to PNG images using svgexport CLI."""
    
    name: str = "svg_to_png"
    description: str = "Converts SVG diagram code to a PNG image file using svgexport CLI"
    args_schema: Type[BaseModel] = SVGExportToolInput
    
    def _run(self, svg_code: str, output_path: str) -> str:
        """
        Run the tool to convert SVG diagram code to PNG using svgexport.
        
        Args:
            svg_code: The SVG diagram code as string
            output_path: Path where the output PNG file will be saved
            
        Returns:
            str: A message indicating success or failure
        """
        svgexport_path = shutil.which("svgexport")
        if not svgexport_path:
            error_msg = "svgexport executable not found. Make sure svgexport is installed globally via npm."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        temp_file_path = None
        try:
            fd, temp_file_path = tempfile.mkstemp(suffix='.svg')
            os.close(fd)
            
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(svg_code)
            
            logger.info(f"Content written to temp file: {svg_code[:100]}...")  # Log first 100 chars
            
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            command = f'"{svgexport_path}" "{temp_file_path}" "{output_path}" png'
            logger.info(f"Executing command: {command}")
            
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
            
            success_msg = f"Successfully converted SVG diagram to {output_path}"
            logger.info(success_msg)
            logger.info(f"Command output: {stdout}")
            return success_msg
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Error converting SVG diagram: Command '{command}' returned non-zero exit status {e.returncode}."
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
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
    
    async def _arun(self, svg_code: str, output_path: str) -> str:
        """Async version of _run method."""
        return self._run(svg_code=svg_code, output_path=output_path)
    
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

def create_svg_export_tool() -> SVGExportTool:
    """Factory function to create a SVGExportTool instance."""
    return SVGExportTool()

if __name__ == "__main__":
    tool = create_svg_export_tool()
    svg_code = """<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#ff6b6b;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#4ecdc4;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect x="10" y="10" width="280" height="180" rx="20" fill="url(#grad1)"/>
        <path d="M100,160 L120,120 L140,160 L160,120 L180,160" fill="none" stroke="white" stroke-width="4"/>
        <text x="150" y="80" text-anchor="middle" fill="white" font-size="24" font-family="Arial">Creative SVG</text>
    </svg>"""
    output_path = "output/svg_diagram.png"
    result = tool._run(svg_code=svg_code, output_path=output_path)
    print(result)