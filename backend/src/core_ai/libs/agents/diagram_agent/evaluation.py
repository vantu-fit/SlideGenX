"""
Evaluation functions for the Diagram Agent.
"""

import logging
from typing import Dict, Any, List

from core_ai.libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)


def evaluate_diagram_completeness(diagram_spec: Dict[str, Any]) -> float:
    """
    Evaluate the completeness of a diagram specification.
    
    Args:
        diagram_spec: The diagram specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating completeness
    """
    score = 0.0
    max_score = 5.0
    
    # Check for essential elements
    if diagram_spec.get("diagram_type"):
        score += 1.0
    
    if diagram_spec.get("title"):
        score += 1.0
    
    components = diagram_spec.get("components", [])
    if components and len(components) > 0:
        score += 1.0
        
        # Bonus points for more components (up to a reasonable limit)
        if len(components) >= 5:
            score += 0.5
    
    connections = diagram_spec.get("connections", [])
    if connections and len(connections) > 0:
        score += 1.0
        
        # Bonus points for more connections (up to a reasonable limit)
        if len(connections) >= 5:
            score += 0.5
    
    # Check for notes/descriptions
    if diagram_spec.get("notes"):
        score += 0.5
    
    # Normalize score to be between 0 and 1
    return min(1.0, score / max_score)


def evaluate_diagram_coherence(diagram_spec: Dict[str, Any]) -> float:
    """
    Evaluate the coherence of a diagram specification.
    
    Args:
        diagram_spec: The diagram specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating coherence
    """
    components = diagram_spec.get("components", [])
    connections = diagram_spec.get("connections", [])
    
    if not components or not connections:
        return 0.0
    
    # Extract component IDs
    component_ids = [c.get("id") for c in components if isinstance(c, dict) and "id" in c]
    
    if not component_ids:
        return 0.0
    
    # Check if connections reference valid components
    valid_connections = 0
    for connection in connections:
        if not isinstance(connection, dict):
            continue
            
        source = connection.get("source")
        target = connection.get("target")
        
        if source in component_ids and target in component_ids:
            valid_connections += 1
    
    # Calculate coherence score
    if not connections:
        return 0.0
        
def evaluate_diagram_complexity(diagram_spec: Dict[str, Any]) -> float:
    """
    Evaluate the complexity of a diagram specification.
    
    Args:
        diagram_spec: The diagram specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating appropriate complexity
    """
    components = diagram_spec.get("components", [])
    connections = diagram_spec.get("connections", [])
    
    # Count components and connections
    num_components = len(components)
    num_connections = len(connections)
    
    # Calculate total elements
    total_elements = num_components + num_connections
    
    # Too few elements is not good
    if total_elements < 3:
        return 0.3
    
    # Too many elements can be overwhelming
    if total_elements > 20:
        return 0.5
    
    # Ideal range is about 5-15 elements total
    if 5 <= total_elements <= 15:
        return 1.0
    
    # Scale linearly between ranges
    if 3 <= total_elements < 5:
        return 0.3 + (total_elements - 3) * 0.35  # Scale from 0.3 to 1.0
    
    if 15 < total_elements <= 20:
        return 1.0 - (total_elements - 15) * 0.1  # Scale from 1.0 to 0.5
    
    return 0.5  # Default case


def evaluate_diagram_appropriateness(diagram_spec: Dict[str, Any], slide_title: str, slide_content: str) -> float:
    """
    Evaluate how appropriate the diagram type is for the content.
    
    Args:
        diagram_spec: The diagram specification to evaluate
        slide_title: The title of the slide
        slide_content: The content of the slide
        
    Returns:
        A score between 0 and 1 indicating appropriateness
    """
    diagram_type = diagram_spec.get("diagram_type", "").lower()
    
    # If no diagram type specified, low score
    if not diagram_type:
        return 0.2
    
    # Combined slide text
    slide_text = (slide_title + " " + slide_content).lower()
    
    # Check for process-related keywords
    process_keywords = ["process", "step", "workflow", "flow", "sequence", "procedure"]
    is_process_related = any(keyword in slide_text for keyword in process_keywords)
    
    # Check for relationship-related keywords
    relationship_keywords = ["relationship", "connection", "link", "network", "interaction", "depends"]
    is_relationship_related = any(keyword in slide_text for keyword in relationship_keywords)
    
    # Check for hierarchy-related keywords
    hierarchy_keywords = ["hierarchy", "structure", "organization", "tree", "level", "category"]
    is_hierarchy_related = any(keyword in slide_text for keyword in hierarchy_keywords)
    
    # Check for comparison-related keywords
    comparison_keywords = ["comparison", "versus", "compare", "contrast", "difference", "similarity"]
    is_comparison_related = any(keyword in slide_text for keyword in comparison_keywords)
    
    # Score based on matching diagram type to content
    score = 0.5  # Default score
    
    # Process diagrams
    if diagram_type in ["flowchart", "process", "workflow", "sequence"]:
        if is_process_related:
            score = 1.0
        elif is_relationship_related:
            score = 0.7
        else:
            score = 0.5
    
    # Relationship diagrams
    elif diagram_type in ["network", "relationship", "entity-relationship", "connection"]:
        if is_relationship_related:
            score = 1.0
        elif is_process_related or is_hierarchy_related:
            score = 0.7
        else:
            score = 0.5
    
    # Hierarchy diagrams
    elif diagram_type in ["hierarchy", "tree", "organization", "mindmap"]:
        if is_hierarchy_related:
            score = 1.0
        elif is_relationship_related:
            score = 0.7
        else:
            score = 0.5
    
    # Comparison diagrams
    elif diagram_type in ["comparison", "venn", "matrix", "quadrant"]:
        if is_comparison_related:
            score = 1.0
        else:
            score = 0.6
    
    return score


def evaluate_diagram_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple diagram agent responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    # Filter out error responses
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid diagram responses to evaluate")
        return None
    
    # If only one valid response, return it
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    # Evaluate each response
    scored_responses = []
    
    for response in valid_responses:
        diagram_spec = response.data
        metadata = response.metadata or {}
        
        # Get slide information from metadata
        slide_title = metadata.get("slide_title", "")
        slide_content = metadata.get("slide_content", "")
        
        # Calculate scores for different criteria
        completeness = evaluate_diagram_completeness(diagram_spec)
        coherence = evaluate_diagram_coherence(diagram_spec)
        complexity = evaluate_diagram_complexity(diagram_spec)
        appropriateness = evaluate_diagram_appropriateness(diagram_spec, slide_title, slide_content)
        
        # Calculate weighted total score
        # Weights can be adjusted based on importance
        total_score = (
            completeness * 0.3 + 
            coherence * 0.3 + 
            complexity * 0.2 + 
            appropriateness * 0.2
        )
        
        # Add to scored responses
        scored_responses.append((response, total_score))
        
        # Log evaluation
        logger.info(f"Diagram evaluation - Completeness: {completeness:.2f}, "
                    f"Coherence: {coherence:.2f}, Complexity: {complexity:.2f}, "
                    f"Appropriateness: {appropriateness:.2f}, Total: {total_score:.2f}")
    
    # Sort by score (descending) and get the best response
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    # Log the selected response
    logger.info(f"Selected diagram spec with score {best_score:.2f}")
    
    return best_response