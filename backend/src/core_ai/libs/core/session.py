"""
Session management for the Tree of Thought slide generation system.
Includes draft management with JSON import/export capabilities.
"""

import uuid
import json
import os
import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime


logger = logging.getLogger(__name__)


class OutputMessage:
    """Class for managing output messages during a session."""

    def __init__(self):
        self.messages = []

    def add(self, message: str, level: str = "info"):
        """
        Add a message to the output messages list.

        Args:
            message: The message text
            level: Message level (info, warning, error, debug)
        """
        self.messages.append({"text": message, "level": level})

        # Also log the message
        if level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "error":
            logger.error(message)
        elif level == "debug":
            logger.debug(message)

    def get_all(self) -> List[Dict[str, str]]:
        """Get all messages."""
        return self.messages

    def clear(self):
        """Clear all messages."""
        self.messages = []


class Draft(BaseModel):
    """Model for storing draft content from each agent."""

    # Agent that created this draft
    agent_name: str

    # Step in the process where this draft was created
    step: str

    # The actual content (could be dict, string, or other data)
    content: Any

    # Timestamp when the draft was created
    created_at: float

    # Metadata about the draft (optional)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Status of the draft (e.g., "created", "approved", "rejected", "revised")
    status: str = "created"

    # Version of the draft (useful for tracking revisions)
    version: int = 1

    # Comments or feedback on the draft
    comments: List[Dict[str, Any]] = Field(default_factory=list)


class CLassifyLayout(BaseModel):
    title: List[int] = Field(description="List of layout indices for title slides")
    agenda: List[int] = Field(description="List of layout indices for agenda slides")
    chapter_title: List[int] = Field(description="List of layout indices for chapter title slides")
    chapter: List[int] = Field(description="List of layout indices for chapter content slides")
    conclusion: List[int] = Field(description="List of layout indices for conclusion slides")
    qa: List[int] = Field(description="List of layout indices for Q&A slides")


class Assest(BaseModel):
    """Asset for storing assets."""

    image_folder: str = Field(
        description="Path to the folder where images are stored",
        default="assets/image_folder",
    )
    diagram_folder: str = Field(
        description="Path to the folder where diagrams are stored",
        default="assets/diagram_folder",
    )


class Artifact(BaseModel):
    """Model for storing artifacts."""

    outline: Dict[str, Any] = Field(
        description="Outline of the presentation", default={}
    )
    sections: List[Dict[str, Any]] = Field(
        description="Sections in the presentation", default=[]
    )
    slides: List[Dict[str, Any]] = Field(
        description="Slides in the presentation", default=[]
    )
    style: Dict[str, Any] = Field(
        description="Style information for the presentation", default={}
    )


class Visual(BaseModel):
    """Model for visual content"""
    path: str = Field(description="Path to the visual file", default="")
    content: str = Field(description="Content of the visual", default={})


class Slide(BaseModel):
    """Model for individual slide content"""

    section_index: int = Field(
        description="Index of the section to which this slide belongs", default=0
    )
    slide_index: int = Field(description="Index of the slide in the section", default=0)
    path: str = Field(description="Path to the slide file", default="")
    content: Dict[str, Any] = Field(description="Content of the slide", default={})
    images: List[Visual] = Field(
        description="List of images and associated with the slide", default=[]
    )
    diagrams: List[Visual] = Field(
        description="List of diagrams associated with the slide", default=[]
    )
class Section(BaseModel):
    """Model for individual section content"""

    title : str = Field(description="Title of the section", default="")
    description : str = Field(description="Description of the section", default="")
    key_points : List[str] = Field(
        description="Key points to be covered in the section", default=[]
    )
    estimated_slides : int = Field(
        description="Estimated number of slides for the section", default=0
    )

    section_index: int = Field(
        description="Index of the section in the presentation", default=0
    )
    section_type:  str = Field(description="title, agenda, chapter, conclustion, qa", default="chaper")
    
    

class Outline(BaseModel):
    """Model for the outline of the presentation."""

    topic: str = Field(description="Topic of the presentation", default="")
    num_sections: int = Field(
        description="Number of sections in the presentation", default=0
    )
    num_slides: int = Field(
        description="Number of slides in the presentation", default=0
    )
    sections: List[Section] = Field(
        description="List of sections in the presentation", default=[]
    )
    


    def json_to_section(self, section: Dict[str, Any]) -> Section:
        """Convert JSON section to Section model"""
        return Section(
            title=section.get("title", ""),
            description=section.get("description", ""),
            key_points=section.get("key_points", []),
            estimated_slides=section.get("estimated_slides", 0),
            section_index=section.get("section_index", 0),
            section_type = section.get("section_type", "chapter")
        )


    def from_outline_agent(self, outline: Dict[str, Any]):
        """Set the outline from the outline agent"""
        self.topic = outline.get("title", "")
        self.num_sections = len(outline.get("sections", []))
        self.num_slides = outline.get("total_slides", 0)
        self.sections = [
            self.json_to_section(section) for section in outline.get("sections", [])
        ]


    
class UserInput(BaseModel):
    """Model for user input."""

    topic: str = Field(description="Topic of the presentation", default="")
    audience: str = Field(description="Audience for the presentation", default="")
    purpose: str = Field(description="Purpose of the presentation", default="")
    presentation_title : str = Field(
        description="Title of the presentation", default=""
    )
    details :Optional[Any] = Field(
        description="Details of the presentation", default=None
    )
    template_path : str = Field(
        description="Path to the template file", default="pptx_templates/Bosch-WeeklyReport.pptx"
    )

class Memory(BaseModel):
    """Model for storing memory."""

    slide_temp_path: str = Field(
        description="Path to the temporary folder for slides", default="temp/slides"
    )
    slides: List[Slide] = Field(
        description="List of slides in the presentation", default=[]
    )
    outline: Outline = Field(
        description="Outline of the presentation", default=Outline()
    )
    user_input : UserInput = Field(
        description="User input for the presentation", default=UserInput()
    )
    slide_layouts : Union[CLassifyLayout, Any] = Field(
        description="Layout information for the slides", default=None
    )

    slide_layout_txt : str = Field(
        description="Layout type of the slide", default=""
    )

    def update_mermaid_code_by_index(self, section_index: int, slide_index: int, mermaid_code: str):
        """Update the mermaid code for a specific slide"""
        for slide in self.slides:
            if slide.section_index == section_index and slide.slide_index == slide_index:
                slide.diagrams[0].content = mermaid_code
                return True

    def update_svg_code_by_index(self, section_index: int, slide_index: int, svg_code: str):  
        """Update the SVG code for a specific slide"""  
        for slide in self.slides:  
            if slide.section_index == section_index and slide.slide_index == slide_index:  
                slide.diagrams[0].content = svg_code  
                return True


    def user_input_from_json(self, user_input: Dict[str, Any]):
        """Set the user input from JSON"""
        self.user_input.topic = user_input.get("topic", "")
        self.user_input.audience = user_input.get("audience", "")
        self.user_input.purpose = user_input.get("purpose", "")
        self.user_input.presentation_title = user_input.get("presentation_title", "")
        self.user_input.details = user_input.get("details", None)
        self.user_input.template_path = user_input.get("template_path", "pptx_templates/Bosch-WeeklyReport.pptx")
        return self.user_input

    def get_slides_by_section_index(self, section_index: int) -> List[Slide]:
        """
        Get slides by section index
        Then sort by slide index
        Args:
            section_index: The index of the section to filter by
        """
        slides = [
            slide for slide in self.slides if slide.section_index == section_index
        ]
        return sorted(slides, key=lambda x: x.slide_index)

    def get_slide_by_index(self, section_index: int, slide_index: int) -> Optional[Slide]:
        """Get slide by section and slide index"""
        for slide in self.slides:
            if slide.section_index == section_index and slide.slide_index == slide_index:
                return slide
        return None

    def get_session_by_index(self, index: int) -> Optional[Section]:
        """Get session by index"""
        if 0 <= index < len(self.outline.sections):
            for section in self.outline.sections:
                if section.section_index == index:
                    return section
        return None

    def slides_from_agent(self, slides: List[Dict[str, Any]]):
        """Set the slides from the slide agent"""
        try:
            for slide in slides:
                self.slides.append(
                    Slide(
                        section_index=slide.get("section_index", 0),
                        slide_index=slide.get("slide_index", 0),
                        path=os.path.join(
                            self.slide_temp_path,
                            f"slide_{slide.get('section_index', 0)}_{slide.get('slide_index', 0)}.pptx",
                        ),
                        images=[Visual(
                            path=os.path.join(
                                self.slide_temp_path,
                                f"image_{slide.get('section_index', 0)}_{slide.get('slide_index', 0)}.png",
                            ),
                            content=image
                        ) for image in slide.get("images_needed", [])],
                        diagrams=[Visual(
                            path=os.path.join(
                                self.slide_temp_path,
                                f"diagram_{slide.get('section_index', 0)}_{slide.get('slide_index', 0)}.png",
                            ),
                            content=diagram["data"]
                        ) for diagram in slide.get("diagrams_needed", [])],
                        content={
                            "title": slide.get("title", ""),
                            "content": slide.get("content", ""),
                            "layout": slide.get("layout", ""),
                            "notes": slide.get("notes", ""),
                            "keywords": slide.get("keywords", []),
                            "layout_type": slide.get("layout_type", ""),
                        },
                    )
                )
        except Exception as e:
            logger.error(f"Error setting slides from agent: {str(e)}")
            raise e

    def save_to_json(self, file_path: Optional[str] = None) -> str:
        """
        Save the memory to a JSON file.

        Args:
            file_path: Path where to save the file. If None, a default path will be created.

        Returns:
            The path where the file was saved
        """
        import time
        from datetime import datetime

        # Create default file path if not provided
        if file_path is None:
            # Create memory directory if it doesn't exist
            memory_dir = os.path.join(os.getcwd(), "temp", "memory")
            os.makedirs(memory_dir, exist_ok=True)

            # Format timestamp for filename
            timestamp = datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(memory_dir, f"memory_{timestamp}.json")

        # Convert memory to dict for serialization
        memory_dict = self.model_dump()

        # Write to file with pretty formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(memory_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved memory to {file_path}")
        return file_path


class SessionState(BaseModel):
    """Model for storing session state."""

    # Current step in the process
    current_step: str = "init"

    save_prompt_folder : str = Field(default="temp/prompt")

    # Data for the current session
    data: Dict[str, Any] = Field(default_factory=dict)

    # Generated artifacts
    artifacts: Artifact = Field(default_factory=Artifact)

    # Drafts from agents
    drafts: List[Draft] = Field(default_factory=list)

    # Errors encountered
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    assets: Assest = Field(default_factory=Assest)

    requirements: Dict[str, Any] = Field(default_factory=dict)



class Session:
    """
    Session management for slide generation process.
    Maintains state throughout the generation process.
    """

    def __init__(
        self, session_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ):
        # Create a unique session ID if none provided
        self.session_id = session_id or str(uuid.uuid4())

        # Store configuration
        self.config = config or {}

        # Create a new output message handler
        self.output_message = OutputMessage()

        # Initialize session state
        self.state = SessionState()

        # Session metadata
        self.metadata = {}

        # Creation timestamp
        self.created_at = None

        # Last updated timestamp
        self.updated_at = None

        self.memory: Memory = Memory()

        # Initialize the session
        self._initialize()

    def save_prompt(self, key: int, type: str, prompt: str):
        """
        Save a prompt to the session's storage in a subfolder based on type.
        
        Args:
            key: The key for the prompt file name
            type: The type of the prompt (e.g., 'section', 'slide')
            prompt: The prompt content to save
        """
        # Create a subfolder for the type if it doesn't exist
        type_folder = os.path.join(self.state.save_prompt_folder, type)
        os.makedirs(type_folder, exist_ok=True)
        
        # Create a filename based on the key
        filename = f"{key}.txt"
        file_path = os.path.join(type_folder, filename)
        
        # Save the prompt to a file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        # Log the action
        self.output_message.add(f"Saved {type} prompt to {file_path}", level="info")
        """
        Save a prompt to the session's storage.
        
        Args:
            type: The type of the prompt (e.g., 'section', 'slide')
            prompt: The prompt content to save
        """
        # Ensure the prompt folder exists
        os.makedirs(self.state.save_prompt_folder, exist_ok=True)
        
        # Create a filename based on the type and current timestam
        
        # Log the action
        self.output_message.add(f"Saved {type} prompt to {file_path}", level="info")
        


    # Requitemnts methods
    def update_requirements(self, key: str, val: Any):
        """Update requiremnets"""
        self.state.requirements[key] = val

    def init_requirements(self, dict: Dict):
        """Init Requirements"""
        self.state.requirements = dict

    def get_requirement(self, key: str):
        """Get requiremnet by key"""
        return self.state.requirements.get(key)

    def get_requiremnets(self):
        return self.state.requirements

    # Artifact methods
    def artifact_add_outline(self, outline: Dict[str, Any]):
        """Add outline to artifact"""
        logger.info(f"Adding outline to artifact")
        self.state.artifacts.outline = outline

    def artifact_add_sections(self, slides: List[Dict[str, Any]]):
        """Add sections to artifact"""
        logger.info(f"Adding sections to artifact")
        self.state.artifacts.sections.extend(slides)

    def artifact_add_slide(self, slides: Dict[str, Any]):
        """Add slides to artifact"""
        logger.info(f"Adding slides to artifact")
        self.state.artifacts.slides.append(slides)

    def artifact_update_slide(self, slides: Dict[str, Any], index: int):
        """Update slides in artifact"""
        if index < len(self.state.artifacts.slides):
            self.state.artifacts.slides[index] = slides
        else:
            self.output_message.add(f"Slide index {index} out of range", level="error")

    def artifact_add_style(self, style: Dict[str, Any]):
        """Add style to artifact"""
        self.state.artifacts.style = style

    def save_artifact(self, file_path: Optional[str] = None) -> str:
        """
        Save the artifact to a JSON file.

        Args:
            file_path: Path where to save the file. If None, a default path will be created.

        Returns:
            The path where the file was saved
        """
        import time
        import json
        import os
        from datetime import datetime

        # Create default file path if not provided
        if file_path is None:
            # Create artifacts directory if it doesn't exist
            artifacts_dir = os.path.join(os.getcwd(), "artifacts")
            os.makedirs(artifacts_dir, exist_ok=True)

            # Format timestamp for filename
            timestamp = datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                artifacts_dir, f"artifact_{self.session_id}_{timestamp}.json"
            )

        # Convert artifact to dict for serialization, ensuring all elements are JSON serializable
        def serialize_object(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            elif isinstance(obj, (list, tuple)):
                return [serialize_object(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: serialize_object(v) for k, v in obj.items()}
            else:
                # For basic types (str, int, bool, etc.)
                # Check if the object is JSON serializable
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, OverflowError):
                    return str(obj)  # Convert non-serializable objects to strings

        # Serialize each component
        outline_data = serialize_object(self.state.artifacts.outline)
        sections_data = serialize_object(self.state.artifacts.sections)
        slides_data = serialize_object(self.state.artifacts.slides)
        style_data = serialize_object(self.state.artifacts.style)

        json_data = {
            "outline": outline_data,
            "sections": sections_data,
            "slides": slides_data,
            "style": style_data,
        }

        # Write to file with pretty formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved artifact to {file_path}")
        return file_path

    def _initialize(self):
        """Initialize the session."""
        import time

        self.created_at = time.time()
        self.updated_at = self.created_at

        logger.info(f"Session {self.session_id} initialized")

    def update_state(self, **kwargs):
        """
        Update the session state.

        Args:
            **kwargs: Key-value pairs to update in the state
        """
        import time

        # Update the state
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
            else:
                self.state.data[key] = value

        # Update the last updated timestamp
        self.updated_at = time.time()

    def get_assets_image_folder(self) -> str:
        """Get the image folder path from assets."""
        return self.state.assets.image_folder

    def get_assets_diagram_folder(self) -> str:
        """Get the diagram folder path from assets."""
        return self.state.assets.diagram_folder

    def add_draft(
        self,
        agent_name: str,
        step: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a draft to the session.

        Args:
            agent_name: Name of the agent that created the draft
            step: The step in the process where this draft was created
            content: The draft content
            metadata: Optional metadata about the draft

        Returns:
            Draft ID (index in the drafts list)
        """
        import time

        # Create a new draft
        draft = Draft(
            agent_name=agent_name,
            step=step,
            content=content,
            created_at=time.time(),
            metadata=metadata or {},
        )

        # Add to drafts list
        self.state.drafts.append(draft)

        # Return the draft ID (index in the list)
        draft_id = len(self.state.drafts) - 1

        # Log the action
        self.output_message.add(
            f"Draft created by {agent_name} for step '{step}' (ID: {draft_id})",
            level="info",
        )

        return str(draft_id)

    def get_draft(self, draft_id: str) -> Optional[Draft]:
        """
        Get a draft by ID.

        Args:
            draft_id: The draft ID (index in the drafts list)

        Returns:
            The draft, or None if not found
        """
        try:
            index = int(draft_id)
            if 0 <= index < len(self.state.drafts):
                return self.state.drafts[index]
        except (ValueError, IndexError):
            pass

        return None

    def update_draft(
        self,
        draft_id: str,
        content: Optional[Any] = None,
        status: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update an existing draft.

        Args:
            draft_id: The draft ID to update
            content: New content (if provided)
            status: New status (if provided)
            comment: Comment to add (if provided)
            metadata: Metadata to update or add (if provided)

        Returns:
            Boolean indicating success
        """
        import time

        draft = self.get_draft(draft_id)
        if not draft:
            self.output_message.add(
                f"Draft with ID {draft_id} not found", level="error"
            )
            return False

        # Update content if provided (creates a new version)
        if content is not None:
            draft.content = content
            draft.version += 1

        # Update status if provided
        if status is not None:
            draft.status = status

        # Add comment if provided
        if comment is not None:
            draft.comments.append({"text": comment, "timestamp": time.time()})

        # Update metadata if provided
        if metadata is not None:
            draft.metadata.update(metadata)

        self.output_message.add(
            f"Draft {draft_id} updated (version: {draft.version}, status: {draft.status})",
            level="info",
        )

        return True

    def get_drafts_by_step(self, step: str) -> List[Draft]:
        """
        Get all drafts for a specific step.

        Args:
            step: The step to filter by

        Returns:
            List of drafts for the specified step
        """
        return [draft for draft in self.state.drafts if draft.step == step]

    def get_drafts_by_agent(self, agent_name: str) -> List[Draft]:
        """
        Get all drafts from a specific agent.

        Args:
            agent_name: The agent name to filter by

        Returns:
            List of drafts from the specified agent
        """
        return [draft for draft in self.state.drafts if draft.agent_name == agent_name]

    def get_latest_draft(
        self, agent_name: str = None, step: str = None
    ) -> Optional[Draft]:
        """
        Get the most recent draft, optionally filtered by agent and/or step.

        Args:
            agent_name: Optional agent name to filter by
            step: Optional step to filter by

        Returns:
            The most recent draft matching the criteria, or None if no drafts found
        """
        drafts = self.state.drafts

        if agent_name:
            drafts = [d for d in drafts if d.agent_name == agent_name]

        if step:
            drafts = [d for d in drafts if d.step == step]

        if not drafts:
            return None

        # Return the most recent draft (assuming drafts are added in chronological order)
        return drafts[-1]

    def save_drafts_to_json(self, file_path: Optional[str] = None) -> str:
        """
        Save all drafts to a JSON file.

        Args:
            file_path: Path where to save the file. If None, a default path will be created.

        Returns:
            The path where the file was saved
        """
        import time
        from datetime import datetime

        # Create default file path if not provided
        if file_path is None:
            # Create drafts directory if it doesn't exist
            drafts_dir = os.path.join(os.getcwd(), "drafts")
            os.makedirs(drafts_dir, exist_ok=True)

            # Format timestamp for filename
            timestamp = datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                drafts_dir, f"drafts_{self.session_id}_{timestamp}.json"
            )

        # Convert drafts to dict for serialization
        drafts_data = []
        for draft in self.state.drafts:
            # Convert draft to dict and ensure all values are JSON serializable
            draft_dict = draft.dict()
            # Format timestamps for better readability
            draft_dict["created_at_formatted"] = datetime.fromtimestamp(
                draft.created_at
            ).strftime("%Y-%m-%d %H:%M:%S")
            # Format comment timestamps
            for comment in draft_dict["comments"]:
                if "timestamp" in comment:
                    comment["timestamp_formatted"] = datetime.fromtimestamp(
                        comment["timestamp"]
                    ).strftime("%Y-%m-%d %H:%M:%S")

            drafts_data.append(draft_dict)

        # Prepare metadata
        metadata = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "created_at_formatted": (
                datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at
                else None
            ),
            "updated_at": self.updated_at,
            "updated_at_formatted": (
                datetime.fromtimestamp(self.updated_at).strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at
                else None
            ),
            "draft_count": len(drafts_data),
            "current_step": self.state.current_step,
            "export_timestamp": time.time(),
            "export_timestamp_formatted": datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        # Create the export data structure
        export_data = {"metadata": metadata, "drafts": drafts_data}

        # Write to file with pretty formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.output_message.add(
            f"Saved {len(drafts_data)} drafts to {file_path}", level="info"
        )
        return file_path

    def load_drafts_from_json(self, file_path: str, append: bool = False) -> int:
        """
        Load drafts from a JSON file.

        Args:
            file_path: Path to the JSON file containing drafts
            append: If True, append loaded drafts to existing ones; if False, replace existing drafts

        Returns:
            Number of drafts loaded
        """
        if not os.path.exists(file_path):
            self.output_message.add(f"File not found: {file_path}", level="error")
            return 0

        try:
            # Read the JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract drafts data
            if "drafts" not in data:
                self.output_message.add(
                    "Invalid drafts file format: 'drafts' key not found", level="error"
                )
                return 0

            drafts_data = data["drafts"]

            # Clear existing drafts if not appending
            if not append:
                self.state.drafts = []

            # Convert JSON data to Draft objects and add to session
            imported_count = 0
            for draft_dict in drafts_data:
                # Remove formatted timestamps that we added for readability but aren't part of the model
                if "created_at_formatted" in draft_dict:
                    del draft_dict["created_at_formatted"]

                # Remove formatted timestamps from comments
                for comment in draft_dict.get("comments", []):
                    if "timestamp_formatted" in comment:
                        del comment["timestamp_formatted"]

                # Create Draft object
                try:
                    draft = Draft(**draft_dict)
                    self.state.drafts.append(draft)
                    imported_count += 1
                except Exception as e:
                    self.output_message.add(
                        f"Error importing draft: {str(e)}", level="error"
                    )

            self.output_message.add(
                f"Loaded {imported_count} drafts from {file_path}", level="info"
            )
            return imported_count

        except Exception as e:
            self.output_message.add(f"Error loading drafts: {str(e)}", level="error")
            return 0

    def add_error(
        self, error_message: str, error_data: Optional[Dict[str, Any]] = None
    ):
        """
        Add an error to the session.

        Args:
            error_message: Human-readable error message
            error_data: Additional error data
        """
        import time

        error = {
            "message": error_message,
            "timestamp": time.time(),
            "data": error_data or {},
        }

        self.state.errors.append(error)
        self.output_message.add(error_message, level="error")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the session to a dictionary.

        Returns:
            Dictionary representation of the session
        """
        return {
            "session_id": self.session_id,
            "state": self.state.dict(),
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def get_slide_by_indices(self, section_index: int, slide_index: int):
        """
        Get a specific slide by section and slide indices.
        
        Args:
            section_index: Index of the section
            slide_index: Index of the slide within the section
            
        Returns:
            Slide object or None if not found
        """
        try:
            section_slides = self.memory.get_slides_by_section_index(section_index)
            if section_slides and slide_index < len(section_slides):
                return section_slides[slide_index]
            return None
        except Exception as e:
            logger.error(f"Error getting slide by indices: {str(e)}")
            return None
        
    def load_from_json(self, file_path: str) -> bool:
        """
        Load memory from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Memory file not found: {file_path}")
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Debug: Print loaded data structure
            print(f"DEBUG: Loading data keys: {list(data.keys())}")
            
            # Update memory fields from loaded data
            if "slide_temp_path" in data:
                self.memory.slide_temp_path = data["slide_temp_path"]
            
            if "slides" in data:
                self.memory.slides = [Slide(**slide_data) for slide_data in data["slides"]]
                print(f"DEBUG: Loaded {len(self.memory.slides)} slides")
            
            if "outline" in data:
                self.memory.outline = Outline(**data["outline"])
                print(f"DEBUG: Loaded outline with {self.memory.outline.num_sections} sections")
            else:
                print("DEBUG: No 'outline' key found in data")
            
            if "user_input" in data:
                self.memory.user_input = UserInput(**data["user_input"])
            
            if "slide_layouts" in data and data["slide_layouts"]:
                self.memory.slide_layouts = CLassifyLayout(**data["slide_layouts"])
            
            if "slide_layout_txt" in data:
                self.memory.slide_layout_txt = data["slide_layout_txt"]
            
            logger.info(f"Successfully loaded memory from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading memory from {file_path}: {str(e)}")
            print(f"DEBUG: Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        
