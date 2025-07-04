"""
Main entry point for the Tree of Thought slide generation system.
"""
print("ok")
import os
import sys
import logging
import argparse
import json
from typing import Dict, Any, Optional

from core_ai.libs.core.session import Session
from core_ai.libs.orchestration.orchestrator import TreeOfThoughtOrchestrator
from core_ai.libs.orchestration.slide_edit_orchestrator import SlideEditOrchestrator
from core_ai.libs.config import load_config, TreeOfThoughtConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tot_slide_generator.log')
    ]
)

logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up command line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(description='Generate presentation slides using Tree of Thought.')
    
    parser.add_argument('--topic', '-t', type=str,
                      help='The main topic of the presentation')
    
    parser.add_argument('--audience', '-a', type=str, default='General audience',
                      help='The target audience (e.g., "executives", "technical team")')
    
    parser.add_argument('--duration', '-d', type=int, default=30,
                      help='Presentation duration in minutes')
    
    parser.add_argument('--purpose', '-p', type=str, default='inform',
                      help='Purpose of the presentation (e.g., "inform", "persuade", "educate")')
    
    parser.add_argument('--config', '-c', type=str, default=None,
                      help='Path to configuration file')
    
    parser.add_argument('--output', '-o', type=str, default='presentation.pptx',
                      help='Output file path')
    
    parser.add_argument('--num-agents', '-n', type=int, default=None,
                      help='Number of agents per task (overrides config)')
    
    parser.add_argument('--template', '-x', type=str, default=None,
                      help='Number of agents per task (overrides config)')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    
    # Add additional arguments for slide editing
    parser.add_argument('--edit', action='store_true',
                      help='Enable edit mode for existing presentation')
    
    parser.add_argument('--session-path', type=str,
                      help='Path to existing session file for editing')
    
    parser.add_argument('--section-index', type=int,
                      help='Section index of slide to edit (0-based)')
    
    parser.add_argument('--slide-index', type=int,
                      help='Slide index within section to edit (0-based)')
    
    parser.add_argument('--edit-prompt', type=str,
                      help='Instructions for editing the slide')
    
    parser.add_argument('--merge-output-path', type=str, default=None,
                      help='Path to save merged output after editing slides')
    
    return parser


def save_presentation(presentation: Dict[str, Any], output_path: str) -> bool:
    """
    Save the generated presentation to a file.
    
    Args:
        presentation: The presentation data
        output_path: Path where to save the presentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(presentation, f, ensure_ascii=False, indent=2)
        logger.info(f"Presentation saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save presentation: {e}")
        return False

def edit_slide(session_path: str, 
               section_index: int, 
               slide_index: int, 
               edit_prompt: str, 
               merge_output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Edit a specific slide in an existing presentation.
    
    Args:
        session_path: Path to the session file
        section_index: Index of section containing the slide
        slide_index: Index of slide within the section
        edit_prompt: User's edit instructions
        
    Returns:
        Edit result dictionary
    """
    try:
        session = Session()
        if not session.load_from_json(session_path):
            return {
                "status": "error",
                "message": "Failed to load session",
                "data": {}
            }
        
        config = load_config()
        edit_orchestrator = SlideEditOrchestrator(session, config)
        result = edit_orchestrator.edit_slide(section_index=section_index, 
                                              slide_index=slide_index, 
                                              edit_prompt=edit_prompt,
                                              merge_output_path=merge_output_path)

        return result
    
    except Exception as e:
        logger.error(f"Error editing slide: {str(e)}")
        return {
            "status": "error",
            "message": f"Error editing slide: {str(e)}",
            "data": {}
        }


def main():
    """Main function."""
    # Parse command line arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments if provided
    if args.num_agents:
        config.num_agents_per_task = args.num_agents
    
    if args.edit:
        if not all([args.session_path, args.section_index is not None,
                    args.slide_index is not None, args.edit_prompt]):
            logger.error("Edit mode requires --session-path, --section-index, --slide-index, and --edit-prompt arguments.")
            return 1
        
        result = edit_slide(
            session_path=args.session_path,
            section_index=args.section_index,
            slide_index=args.slide_index,
            edit_prompt=args.edit_prompt,
            merge_output_path=args.merge_output_path
        )

        if result.get("status") == "success":
            print(f"\n=== Slide Edit Successful ===")
            print(f"Section: {args.section_index}")
            print(f"Slide: {args.slide_index}")
            print(f"Edit: {args.edit_prompt}")
            print("============================\n")

            if args.merge_output_path:
                merged_path = result.get("data", {}).get("merged_presentation_path")
                if merged_path:
                    print(f"Merged presentation saved to: {merged_path}")
            else:
                print("Warning: Merge was requested but failed")
            print("============================\n")
            return 0
        else:
            logger.error(f"Failed to edit slide: {result.get('message')}")
            return 1
    
    # Regular generation mode - validate required arguments
    if not args.topic:
        logger.error("Generation mode requires --topic argument.")
        return 1
        
    # Create session
    session = Session()
    
    try:
        # Create orchestrator
        orchestrator = TreeOfThoughtOrchestrator(session, config)
        
        # Generate presentation
        logger.info(f"Generating presentation on topic: {args.topic}")
        presentation = orchestrator.generate_presentation(
            topic=args.topic,
            audience=args.audience,
            duration=args.duration,
            purpose=args.purpose,
            output_path=args.output,
            template_path=args.template
        )
        
        # Save presentation
        if presentation.get("status") == "success":
            
            # Print summary
            print("\n=== Presentation Summary ===")
            print(f"Topic: {args.topic}")
            print(f"Title: {presentation['data']['outline']['title']}")
            print(f"Sections: {len(presentation['data']['outline']['sections'])}")
            print(f"Total Slides: {len(presentation['data']['slides'])}")
            print(f"Output: {args.output}")
            print("===========================\n")
            orchestrator.session.save_artifact()
            return 0
        else:
            logger.error(f"Failed to generate presentation: {presentation.get('message')}")
            return 1
            
    except Exception as e:
        orchestrator.session.save_artifact()
        logger.exception(f"Error generating presentation: {e}")
        return 1

def gen_slide(
    topic: str,
    audience: str = "General audience",
    duration: int = 30,
    purpose: str = "inform",
    output_path: str = "presentation.pptx",
    template_path: Optional[str] = None):
    """
    Generate a presentation slide using the Tree of Thought system.
    
    Args:
        topic: The main topic of the presentation
        audience: The target audience (default: "General audience")
        duration: Presentation duration in minutes (default: 30)
        purpose: Purpose of the presentation (default: "inform")
        output_path: Path to save the generated presentation (default: "presentation.pptx")
        template_path: Optional path to a template for the slides
    
    Returns:
        Result dictionary containing status and data
    """
    args = argparse.Namespace(
        topic=topic,
        audience=audience,
        duration=duration,
        purpose=purpose,
        output=output_path,
        template=template_path,
        verbose=False
    )
    try:
        config = load_config(args.config)
    except Exception as e:
        config = load_config()
    session = Session()
    
    try:
        # Create orchestrator
        orchestrator = TreeOfThoughtOrchestrator(session, config)
        
        # Generate presentation
        logger.info(f"Generating presentation on topic: {args.topic}")
        presentation = orchestrator.generate_presentation(
            topic=args.topic,
            audience=args.audience,
            duration=args.duration,
            purpose=args.purpose,
            output_path=args.output,
            template_path=args.template
        )
        
        # Save presentation
        if presentation.get("status") == "success":
            
            # Print summary
            print("\n=== Presentation Summary ===")
            print(f"Topic: {args.topic}")
            print(f"Title: {presentation['data']['outline']['title']}")
            print(f"Sections: {len(presentation['data']['outline']['sections'])}")
            print(f"Total Slides: {len(presentation['data']['slides'])}")
            print(f"Output: {args.output}")
            print("===========================\n")
            orchestrator.session.save_artifact()
            return 0
        else:
            logger.error(f"Failed to generate presentation: {presentation.get('message')}")
            return 1
            
    except Exception as e:
        orchestrator.session.save_artifact()
        logger.exception(f"Error generating presentation: {e}")
        return 1

if __name__ == "__main__":
    # sys.exit(main())  
    # test gen_slide function
    gen_slide(
        topic="The Future of AI in Healthcare",
        audience="Healthcare Professionals",
        duration=45,
        purpose="educate",
        output_path="future_ai_healthcare.pptx",
        template_path="core_ai/pptx_templates/Geometric.pptx"
    )
