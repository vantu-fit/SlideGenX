"""
Main entry point for the Tree of Thought slide generation system.
"""
print("ok")
import os
import sys
import logging
import argparse
import json
from typing import Dict, Any

from libs.core.session import Session
from libs.orchestration.orchestrator import TreeOfThoughtOrchestrator
from libs.config import load_config, TreeOfThoughtConfig

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
    
    parser.add_argument('--topic', '-t', type=str, required=True,
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


if __name__ == "__main__":
    sys.exit(main())  
