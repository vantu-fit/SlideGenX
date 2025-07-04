"""
Evaluation functions for the SVG Diagram Agent.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

from core_ai.libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)

def evaluate_svg_completeness(svg_spec: Dict[str, Any]) -> float:
    """
    Evaluate the completeness of an SVG diagram specification.
    
    Args:
        svg_spec: The SVG diagram specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating completeness
    """
    score = 0.0
    max_score = 5.0
    
    # Check for essential elements
    if svg_spec.get("diagram_type"):
        score += 1.0
    
    if svg_spec.get("title"):
        score += 1.0
    
    # Check SVG code for key elements
    svg_code = svg_spec.get("svg_code", "")
    if svg_code:
        try:
            root = ET.fromstring(svg_code)
            # Check for presence of graphical elements (rect, circle, path, etc.)
            graphical_elements = len(root.findall(".//{http://www.w3.org/2000/svg}rect") +
                                  root.findall(".//{http://www.w3.org/2000/svg}circle") +
                                  root.findall(".//{http://www.w3.org/2000/svg}path") +
                                  root.findall(".//{http://www.w3.org/2000/svg}line"))
            if graphical_elements > 0:
                score += 1.0
                # Bonus for sufficient number of elements
                if graphical_elements >= 5:
                    score += 0.5
        except ET.ParseError:
            logger.warning("Invalid SVG code detected during completeness evaluation")
    
    # Check for connections or relationships (e.g., lines or paths)
    if svg_code and "line" in svg_code or "path" in svg_code:
        score += 1.0
        # Bonus for multiple connections
        if svg_code.count("line") + svg_code.count("path") >= 5:
            score += 0.5
    
    # Check for notes/explanation
    if svg_spec.get("explanation"):
        score += 0.5
    
    # Normalize score to be between 0 and 1
    return min(1.0, score / max_score)

def evaluate_svg_coherence(svg_spec: Dict[str, Any]) -> float:  
    """  
    Evaluate the coherence of an SVG diagram specification.  
      
    Args:  
        svg_spec: The SVG diagram specification to evaluate  
          
    Returns:  
        A score between 0 and 1 indicating coherence  
    """  
    svg_code = svg_spec.get("svg_code", "")  
    if not svg_code:  
        return 0.0  
      
    try:  
        root = ET.fromstring(svg_code)  
        # Extract IDs of elements  
        elements_with_id = root.findall(".//*[@id]")  
        element_ids = [elem.get("id") for elem in elements_with_id if elem.get("id")]  
          
        if not element_ids:  
            return 0.0  
        
        # Check for connections (lines or paths referencing elements)
        connections = root.findall(".//{http://www.w3.org/2000/svg}line") + \
                     root.findall(".//{http://www.w3.org/2000/svg}path")
        
        valid_connections = 0  
        for conn in connections:  
            # Simple heuristic: assume lines/paths indicate relationships  
            if conn.get("x1") and conn.get("y1") and conn.get("x2") and conn.get("y2"):  
                valid_connections += 1  
          
        # Calculate base coherence based on valid connections and elements  
        if not connections:  
            base_coherence_score = 0.0  
        else:  
            base_coherence_score = valid_connections / max(1, len(elements_with_id))  
          
        # Check for SVG quality indicators  
        has_proper_viewbox = 'viewBox' in svg_code    
        has_proper_namespace = 'xmlns' in svg_code      
        uses_groups = '<g' in svg_code  # Indicates organized structure    
        has_gradients = 'linearGradient' in svg_code or 'radialGradient' in svg_code  
  
        quality_bonus = 0.0    
        if has_proper_viewbox:    
            quality_bonus += 0.1    
        if has_proper_namespace:    
            quality_bonus += 0.1    
        if uses_groups:    
            quality_bonus += 0.1    
        if has_gradients:    
            quality_bonus += 0.1    
          
        # Combine base score with quality bonus  
        coherence_score = min(1.0, base_coherence_score + quality_bonus)  
        return coherence_score  
      
    except ET.ParseError:  
        logger.warning("Invalid SVG code detected during coherence evaluation")  
        return 0.0

def evaluate_svg_complexity(svg_spec: Dict[str, Any]) -> float:
    """
    Evaluate the complexity of an SVG diagram specification.
    
    Args:
        svg_spec: The SVG diagram specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating appropriate complexity
    """
    svg_code = svg_spec.get("svg_code", "")
    if not svg_code:
        return 0.3
    
    try:
        root = ET.fromstring(svg_code)
        # Count graphical elements
        elements = (root.findall(".//{http://www.w3.org/2000/svg}rect") +
                   root.findall(".//{http://www.w3.org/2000/svg}circle") +
                   root.findall(".//{http://www.w3.org/2000/svg}path") +
                   root.findall(".//{http://www.w3.org/2000/svg}line") +
                   root.findall(".//{http://www.w3.org/2000/svg}text"))
        
        total_elements = len(elements)
        
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
        
        return 0.5
    
    except ET.ParseError:
        logger.warning("Invalid SVG code detected during complexity evaluation")
        return 0.3

def evaluate_svg_appropriateness(svg_spec: Dict[str, Any], slide_title: str, slide_content: str) -> float:
    """
    Evaluate how appropriate the SVG diagram type is for the content.
    
    Args:
        svg_spec: The SVG diagram specification to evaluate
        slide_title: The title of the slide
        slide_content: The content of the slide
        
    Returns:
        A score between 0 and 1 indicating appropriateness
    """
    diagram_type = svg_spec.get("diagram_type", "").lower()
    
    if not diagram_type:
        return 0.2
    
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
    
    # Check for timeline-related keywords
    timeline_keywords = ["timeline", "history", "chronology", "sequence", "event"]
    is_timeline_related = any(keyword in slide_text for keyword in timeline_keywords)

    # Check for data visualization-related keywords
    data_viz_keywords = ["chart", "graph", "data", "metrics", "performance", "statistics", "analytics"]  
    is_data_viz_related = any(keyword in slide_text for keyword in data_viz_keywords) 
    
    # Score based on matching diagram type to content
    score = 0.5  # Default score
    
    if diagram_type == "flowchart":
        if is_process_related:
            score = 1.0
        elif is_relationship_related:
            score = 0.7
        else:
            score = 0.5
    
    elif diagram_type == "relationship":
        if is_relationship_related:
            score = 1.0
        elif is_process_related or is_hierarchy_related:
            score = 0.7
        else:
            score = 0.5
    
    elif diagram_type == "hierarchy":
        if is_hierarchy_related:
            score = 1.0
        elif is_relationship_related:
            score = 0.7
        else:
            score = 0.5
    
    elif diagram_type == "comparison":
        if is_comparison_related:
            score = 1.0
        else:
            score = 0.6
    
    elif diagram_type == "timeline":
        if is_timeline_related:
            score = 1.0
        elif is_process_related:
            score = 0.7
        else:
            score = 0.5
    
    # Data visualization types  
    elif diagram_type in ["bar", "line", "scatter", "gauge", "donut"]:  
        if is_data_viz_related:  
            score = 1.0  
        else:  
            score = 0.6  
    
    # Specialized types    
    elif diagram_type in ["radar", "sankey", "network"]:  
        if diagram_type == "radar" and any(keyword in slide_text for keyword in ["multi", "variable", "comparison", "analysis"]):  
            score = 1.0  
        elif diagram_type == "sankey" and any(keyword in slide_text for keyword in ["flow", "quantity", "transfer"]):  
            score = 1.0  
        elif diagram_type == "network" and is_relationship_related:  
            score = 1.0  
        else:  
            score = 0.7  
    
    # Mixed types  
    elif diagram_type in ["pie", "mindmap", "quadrant"]:  
        if diagram_type == "pie" and any(keyword in slide_text for keyword in ["proportion", "percentage", "share", "distribution"]):  
            score = 1.0  
        elif diagram_type == "mindmap" and is_hierarchy_related:  
            score = 1.0  
        elif diagram_type == "quadrant" and is_comparison_related:  
            score = 1.0  
        else:  
            score = 0.7
    
    return score

def evaluate_svg_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple SVG diagram agent responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid SVG diagram responses to evaluate")
        return None
    
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    scored_responses = []
    
    for response in valid_responses:
        svg_spec = response.data
        metadata = response.metadata or {}
        
        slide_title = metadata.get("slide_title", "")
        slide_content = metadata.get("slide_content", "")
        
        completeness = evaluate_svg_completeness(svg_spec)
        coherence = evaluate_svg_coherence(svg_spec)
        complexity = evaluate_svg_complexity(svg_spec)
        appropriateness = evaluate_svg_appropriateness(svg_spec, slide_title, slide_content)
        
        # Calculate weighted total score
        total_score = (
            completeness * 0.3 +
            coherence * 0.3 +
            complexity * 0.2 +
            appropriateness * 0.2
        )
        
        scored_responses.append((response, total_score))
        
        logger.info(f"SVG diagram evaluation - Completeness: {completeness:.2f}, "
                    f"Coherence: {coherence:.2f}, Complexity: {complexity:.2f}, "
                    f"Appropriateness: {appropriateness:.2f}, Total: {total_score:.2f}")
    
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    logger.info(f"Selected SVG diagram spec with score {best_score:.2f}")
    
    return best_response