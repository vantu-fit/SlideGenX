"""
Tree of Thought Orchestrator for slide generation.
Manages the overall process of generating presentations using multiple agents.
"""

import logging, time, os,shutil
import concurrent.futures
from typing import List, Dict, Any, Optional, Type

from libs.core.session import Session
from libs.core.agent_response import AgentResponse
from libs.core.agent_status import AgentStatus
from libs.core.base_agent import BaseAgent
from libs.models.slide_models import SlideContent

from libs.agents.outline_agent.agent import OutlineAgent
from libs.agents.outline_agent.evaluation import evaluate_outline_responses

from libs.agents.slide_content_agent.agent import SlideContentAgent
from libs.agents.slide_content_agent.evaluation import evaluate_slide_content_responses

from libs.agents.image_agent.agent import ImageAgent
from libs.agents.image_agent.evaluation import evaluate_image_responses

from libs.agents.diagram_agent.agent import DiagramAgent
from libs.agents.diagram_agent.evaluation import evaluate_diagram_responses

from libs.agents.svg_diagram_agent import SVGDdiagramAgent
from libs.agents.svg_diagram_agent.evaluation import evaluate_svg_responses

from libs.agents.slide_generator_agent.agent import SlideGeneratorAgent
from libs.agents.slide_generator_agent.evaluation import (
    evaluate_slide_generator_responses,
)

from libs.utils.merge_pptx import merge_pptx_files
from libs.utils.create_master import remove_all_slides

from libs.config import TreeOfThoughtConfig
import config.global_config as gcfg
from libs.agents.utils import filter_slide_info

logger = logging.getLogger(__name__)


class GlobalConfig:
    """Global configuration for slide generation."""

    num_agents_per_task: int = 3
    GENERATOR_MODEL_INDEX: int = 0
    max_iterations: int = 3
    temperature: float = 0.7
    enable_parallel: bool = True
    max_workers: int = 4


class SlideGeneratorConfig:
    """Configuration for slide generator agents."""

    llm_index: str = gcfg.GlobalConfig.DEFAULT_MODEL_INDEX


class TreeOfThoughtOrchestrator:
    """
    Orchestrates the Tree of Thought process for slide generation,
    managing multiple agents at each level and selecting the best outputs.
    """

    def __init__(
        self, session: Session, config: Optional[TreeOfThoughtConfig] = None, **kwargs
    ):
        """
        Initialize the Tree of Thought Orchestrator.

        Args:
            session: Session object for the current generation process
            config: Optional configuration
            **kwargs: Additional arguments to pass to agents
        """
        self.agent_name = "tree_of_thought_orchestrator"
        self.description = "Orchestrator for Tree of Thought slide generation"
        self.session = session
        self.config = config or GlobalConfig()
        self.kwargs = kwargs

        # Agent factory method mapping
        self.agent_factories = {
            "outline": OutlineAgent,
            "slide_content": SlideContentAgent,
            "image": ImageAgent,
            "diagram": DiagramAgent,
            "master_slide_generator": SlideGeneratorAgent,
            "svg_diagram": SVGDdiagramAgent,
        }

        # Evaluation function mapping
        self.evaluation_functions = {
            "outline": evaluate_outline_responses,
            "slide_content": evaluate_slide_content_responses,
            "image": evaluate_image_responses,
            "diagram": evaluate_diagram_responses,
            "master_slide_generator": evaluate_slide_generator_responses,
            "svg_diagram": evaluate_svg_responses,
        }

        logger.info(
            f"Initialized TreeOfThoughtOrchestrator with {self.config.num_agents_per_task} agents per task"
        )

    def _determine_diagram_agent_type(self, diagrams_needed: List[str]) -> str:  
        """  
        Determine which diagram agent to use based on diagram types needed.  
        
        Args:  
            diagrams_needed: List of diagram descriptions  
            
        Returns:  
            "diagram" for Mermaid-based diagrams, "svg_diagram" for SVG-based diagrams  
        """  
        # Keywords that indicate Mermaid diagrams  
        mermaid_keywords = ["flowchart", "flow", "class diagram", "sequence", "state", "process"]  
        
        # Keywords that indicate SVG diagrams    
        svg_keywords = ["chart", "graph", "bar", "line", "pie", "scatter", "histogram"]  
        
        diagrams_text = " ".join(diagrams_needed).lower()  
        
        # Check for Mermaid keywords first  
        if any(keyword in diagrams_text for keyword in mermaid_keywords):  
            return "diagram"  
        
        # Check for SVG keywords  
        if any(keyword in diagrams_text for keyword in svg_keywords):  
            return "svg_diagram"  
        
        # Default
        return "diagram"

    def create_agents(self, agent_type: str, count: int) -> List[BaseAgent]:
        """
        Create multiple instances of a specific agent type.

        Args:
            agent_type: Type of agent to create
            count: Number of agents to create

        Returns:
            List of agent instances
        """
        if agent_type not in self.agent_factories:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = self.agent_factories[agent_type]

        # Create the specified number of agents
        agents = []
        for _ in range(count):
            agent = agent_class(self.session, cfg=SlideGeneratorConfig(), **self.kwargs)
            agents.append(agent)

        return agents

    def evaluate_responses(
        self, responses: List[AgentResponse], agent_type: str
    ) -> Optional[AgentResponse]:
        """
        Evaluate multiple agent responses and select the best one.

        Args:
            responses: List of agent responses to evaluate
            agent_type: Type of agent that produced the responses

        Returns:
            The best response, or None if no valid responses
        """
        if self.config.num_agents_per_task == 1:
            return responses[0] if responses else None
        # Use the appropriate evaluation function
        if agent_type in self.evaluation_functions:
            return self.evaluation_functions[agent_type](responses)

        # Fallback to basic evaluation
        valid_responses = [r for r in responses if r.status == AgentStatus.SUCCESS]
        if not valid_responses:
            return None

        return valid_responses[0]

    def run_parallel(
        self, agents: List[BaseAgent], run_args: List[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Run multiple agents in parallel.

        Args:
            agents: List of agents to run
            run_args: List of arguments to pass to each agent's run method

        Returns:
            List of agent responses
        """
        responses = []

        if self.config.enable_parallel:
            # Run agents in parallel
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config.max_workers
            ) as executor:
                # Create futures for each agent
                futures = [
                    executor.submit(agent.safe_call, **args)
                    for agent, args in zip(agents, run_args)
                ]

                # Collect responses as they complete
                for future in concurrent.futures.as_completed(futures):
                    responses.append(future.result())
        else:
            # Run agents sequentially
            for agent, args in zip(agents, run_args):
                responses.append(agent.safe_call(**args))

        return responses

    def generate_presentation_outline(
        self, topic: str, audience: str, duration: int, purpose: str
    ) -> Optional[AgentResponse]:
        """
        First level: Generate multiple presentation outlines and select the best one.

        Args:
            topic: The main topic of the presentation
            audience: The target audience
            duration: Presentation duration in minutes
            purpose: Purpose of the presentation

        Returns:
            The best outline, or None if generation failed
        """
        self.session.output_message.add(
            f"Generating {self.config.num_agents_per_task} outline variations...",
            level="info",
        )

        # Create agents
        agents = self.create_agents("outline", self.config.num_agents_per_task)

        # Prepare arguments for each agent
        run_args = []
        for _ in range(self.config.num_agents_per_task):
            run_args.append(
                {
                    "topic": topic,
                    "audience": audience,
                    "duration": duration,
                    "purpose": purpose,
                }
            )

        # Run agents
        responses = self.run_parallel(agents, run_args)

        # Evaluate responses
        best_outline = self.evaluate_responses(responses, "outline")

        if best_outline:
            self.session.output_message.add(
                "Successfully selected best outline", level="info"
            )
            # Store the outline in the session
            self.session.artifact_add_outline(best_outline.data)
        else:
            self.session.output_message.add(
                "Failed to generate any valid outlines", level="error"
            )

        return best_outline

    def generate_slide_content(self, section_index: int) -> Optional[AgentResponse]:
        """
        Second level: Generate multiple slide contents for each slide and select the best one.

        Args:
            outline: The selected presentation outline
            slide_number: The number of the slide in the presentation
            section: The section this slide belongs to

        Returns:
            The best slide content, or None if generation failed
        """
        self.session.output_message.add(
            f"Generating {self.config.num_agents_per_task} variations for slide ...",
            level="info",
        )

        # Create agent
        agents = self.create_agents("slide_content", self.config.num_agents_per_task)

        run_args = []
        for i in range(self.config.num_agents_per_task):
            run_args.append(
                {
                    "section_index": section_index,
                    "agent_index": i,
                }
            )

        # Run agents
        responses = self.run_parallel(agents, run_args)

        # Evaluate responses
        best_content = self.evaluate_responses(responses, "slide_content")

        if best_content:
            self.session.output_message.add(
                f"Successfully selected best content for section #{section_index}",
                level="info",
            )
            # Store the slide content in the session
            self.session.artifact_add_sections(best_content.data.get("slides", []))
        else:
            self.session.output_message.add(
                f"Failed to generate valid content for section #{section_index}",
                level="error",
            )

        self.session.add_draft(
            agent_name=self.agent_name,
            step="content_selected",
            content=best_content.data,
            metadata=best_content.metadata,
        )
        self.session.save_drafts_to_json("drafts.json")
        self.session.memory.slides_from_agent(best_content.data.get("slides", []))
        return best_content

    def generate_slide_elements(
        self, section: Dict[str, any], slide_content: Dict[str, Any]
    ) -> List[Dict]:
        """
        Third level: Generate specialized elements for each slide.

        Args:
            slide_content: The selected slide content

        Returns:
            Dictionary of specialized elements for the slide
        """
        slides = slide_content.get("slides", [])

        results = []
        for index, slide_content in enumerate(slides):
            slide_content["section_index"] = section.get("section_index")
            slide_content["slide_index"] = index
            # Generate image specifications if needed
            if slide_content.get("images_needed"):
                self.session.output_message.add(
                    f"Generating image specifications...", level="info"
                )

                image_agents = self.create_agents(
                    "image", self.config.num_agents_per_task
                )
                image_run_args = []

                for _ in range(self.config.num_agents_per_task):
                    image_run_args.append(
                        {
                            "slide_title": slide_content.get("title", ""),
                            "slide_content": slide_content.get("content", ""),
                            "image_descriptions": slide_content.get(
                                "images_needed", []
                            ),
                        }
                    )

                image_responses = self.run_parallel(image_agents, image_run_args)
                slide_content["image"] = self.evaluate_responses(
                    image_responses, "image"
                )

                if slide_content["image"]:
                    self.session.output_message.add(
                        "Successfully selected best image specifications", level="info"
                    )
                    # self.session.add_artifact(f"image_specs_{slide_content['slide_number']}", slide_content["image"].data)
                else:
                    self.session.output_message.add(
                        "Failed to generate valid image specifications", level="warning"
                    )

            # Generate diagram specifications if needed
            if slide_content.get("diagrams_needed"):
                self.session.output_message.add(
                    f"Generating diagram specifications...", level="info"
                )
            
                diagram_agent_type = self._determine_diagram_agent_type(
                    slide_content.get("diagrams_needed", [])
                )
                # diagram_agent_type = "svg_diagram"  

                diagram_agents = self.create_agents(
                    diagram_agent_type, self.config.num_agents_per_task
                )
                diagram_run_args = []

                for _ in range(self.config.num_agents_per_task):
                    diagram_run_args.append(
                        {
                            "section_title": section.get("title", ""),
                            "section_description": section.get("description", ""),
                            "slide_title": slide_content.get("title", []),
                            "slide_content": slide_content.get("content", []),
                            "diagrams_needed": slide_content.get("diagrams_needed", []),
                            "slide_keywords": slide_content.get("keywords", []),
                        }
                    )

                diagram_responses = self.run_parallel(diagram_agents, diagram_run_args)
                slide_content["diagram"] = self.evaluate_responses(
                    diagram_responses, diagram_agent_type
                )

                if slide_content["diagram"]:
                    self.session.output_message.add(
                        "Successfully selected best diagram specifications",
                        level="info",
                    )
                    # self.session.add_artifact(f"diagram_specs_{slide_content['slide_number']}", slide_content["diagram"].data)
                else:
                    self.session.output_message.add(
                        "Failed to generate valid diagram specifications",
                        level="warning",
                    )
            results.append(slide_content)

        return results


    def generate_final_slide(self, section_index: int) -> Optional[AgentResponse]:
        """
        Generate the final slide by integrating all elements.

        Args:
            slide_content: The selected slide content
            slide_elements: Dictionary of specialized elements for the slide
            style_specs: Style specifications for the presentation

        Returns:
            The best integrated slide, or None if generation failed
        """
        self.session.output_message.add(
            f"Generating {self.config.num_agents_per_task} integrated versions for slide ...",
            level="info",
        )

        generator_agents = self.create_agents(
            "master_slide_generator", self.config.num_agents_per_task
        )
        generator_run_args = []

        for i in range(self.config.num_agents_per_task):
            generator_run_args.append(
                {
                    "section_index": section_index,
                    "agent_index": i,
                }
            )

        generator_responses = self.run_parallel(generator_agents, generator_run_args)
        best_slide = self.evaluate_responses(
            generator_responses, "master_slide_generator"
        )

        if best_slide:
            self.session.output_message.add(
                f"Successfully generated final for section #{section_index}", level="info"
            )
        else:
            self.session.output_message.add(
                f"Failed to generate final for section #{section_index}", level="error"
            )

        return best_slide

    def generate_presentation( 
        self, topic: str, audience: str, duration: int, purpose: str, output_path : str, template_path: str = "Khai/Geometric-annual-presentation.pptx",
        parallel: bool =  True, pdf : bool = True 
    ) -> Dict[str, Any]: 
        """ 
        Main method to orchestrate the entire presentation generation process. 
 
        Args: 
            topic: The main topic of the presentation 
            audience: The target audience 
            duration: Presentation duration in minutes 
            purpose: Purpose of the presentation
            template_path: Path to the PowerPoint template file
            parallel: Whether to process sections in parallel (True) or sequentially (False)
 
        Returns: 
            A complete presentation with all slides and elements 
        """ 
        if "diagram_drawed" not in self.session.state.requirements: 
            self.session.state.requirements["diagram_drawed"] = [] 
        # if self.session.memory.slide_temp_path then delete 
        if os.path.exists(self.session.memory.slide_temp_path):
            shutil.rmtree(self.session.memory.slide_temp_path)

        if os.path.exists(self.session.state.save_prompt_folder):
            shutil.rmtree(self.session.state.save_prompt_folder)
        os.makedirs(self.session.state.save_prompt_folder, exist_ok=True)
        start_time = time.time() 
        self.session.output_message.add( 
            f"Starting presentation generation on '{topic}'...", level="info" 
        ) 
        # Create template slide
        remove_all_slides(template_path, template_path)
 
        # Init requiremnets for this session 
        requirements = { 
            "topic": topic, 
            "audiencs": audience, 
            "duration": duration, 
            "purpose": purpose, 
            # "template": "pptx_templates/Bosch-WeeklyReport.pptx", 
        } 
 
        self.session.init_requirements(requirements) 
 
        self.session.memory.user_input_from_json({ 
            "topic": topic, 
            "audience": audience, 
            "purpose": purpose, 
            "template_path": template_path, 
        }) 
 
        # Level 1: Generate presentation outline 
        outline_response = self.generate_presentation_outline( 
            topic, audience, duration, purpose 
        ) 
        if not outline_response: 
            return { 
                "status": "error", 
                "message": "Failed to generate presentation outline", 
                "data": {}, 
            } 
 
        outline = outline_response.data 
        self.session.memory.outline.from_outline_agent(outline) 
        self.session.memory.user_input.presentation_title = outline.get("title", topic) 
        logger.info(f"Generated outline with {len(outline['sections'])} sections") 
 
        def process_section(section_index: int) -> Optional[Dict[str, Any]]: 
            section_content = self.generate_slide_content(section_index=section_index) 
            self.session.memory.save_to_json("memory.json") 
            if section_content: 
                final_section_slide = self.generate_final_slide(section_index=section_index) 
                return final_section_slide.data if final_section_slide else None 
            return None 
        
        slides = []
        
        # Choose between parallel and sequential processing based on the parallel parameter
        if parallel:
            # Parallel processing using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config.max_workers
            ) as executor:
                futures = {
                    executor.submit(process_section, section_index): section_index
                    for section_index in range(self.session.memory.outline.num_sections)
                }
                slides = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                    if future.result() is not None
                ]
        else:
            # Sequential processing
            for section_index in range(self.session.memory.outline.num_sections):
                result = process_section(section_index)
                if result is not None:
                    slides.append(result)
                    logger.info(f"Completed processing section {section_index + 1}/{self.session.memory.outline.num_sections}")

        # Log the execution time 
        end_time = time.time() 
        execution_time = end_time - start_time 
        logger.info( 
            f"Presentation generation completed in {execution_time:.2f} seconds" 
        ) 

        # Merge  file
        try:
            merge_pptx_files(input_dir=self.session.memory.slide_temp_path, output_path=output_path)

            logger.info("Successfully merged pptx files")
        except Exception as e:
            logger.error(f"Error merging pptx files: {str(e)}")
 
        return { 
            "status": "success", 
            "message": f"Successfully generated presentation with {len(slides)} slides", 
            "data": { 
                "outline": outline, 
                "slides": slides, 
                "metadata": { 
                    "topic": topic, 
                    "audience": audience, 
                    "duration": duration, 
                    "purpose": purpose, 
                    "total_slides": len(slides), 
                    "parallel_processing": parallel,
                }, 
            }, 
        }
