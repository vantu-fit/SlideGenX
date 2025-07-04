"""
Evaluation functions for the Slide Generator Agent.
"""

import logging
from typing import Dict, Any, List

from core_ai.libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)


def evaluate_slide_completeness(slide_data: Dict[str, Any]) -> float:
    """
    Evaluate the completeness of a generated slide.
    
    Args:
        slide_data: The slide data to evaluate
        
    Returns:
        A score between 0 and 1 indicating completeness
    """
    score = 0.0
    max_score = 5.0
    
    # Check for essential slide elements
    slide_content = slide_data.get("slide_content", {})
    generated_slide = slide_data.get("generated_slide", "")
    
    if slide_content:
        # Check if title is included
        if slide_content.get("title", ""):
            score += 1.0
            
            # Check if title appears in the generated slide
            title = slide_content.get("title", "")
            if title.lower() in generated_slide.lower():
                score += 0.5
        
        # Check if content is included and substantial
        content = slide_content.get("content", "")
        if content and len(content) > 20:  # Arbitrary threshold for meaningful content
            score += 1.0
    
    # Check if generated slide is substantial
    if generated_slide and len(generated_slide) > 100:  # Arbitrary threshold for substantial description
        score += 1.0
    
    # Check if visual elements are integrated
    if any([
        slide_data.get("image_specs"),
        slide_data.get("diagram_specs"),
        slide_data.get("data_viz_specs")
    ]):
        score += 1.0
    
    # Check if style is applied
    if slide_data.get("style_specs"):
        score += 0.5
    
    # Normalize score to be between 0 and 1
    return score / max_score


def evaluate_slide_integration(slide_data: Dict[str, Any]) -> float:
    """
    Evaluate how well the elements are integrated in the slide.
    
    Args:
        slide_data: The slide data to evaluate
        
    Returns:
        A score between 0 and 1 indicating integration quality
    """
    generated_slide = slide_data.get("generated_slide", "").lower()
    
    # Check if the integration description mentions key terms related to layout and design
    integration_terms = [
        "layout", "integrate", "placement", "position", "arrange", "balance",
        "composition", "harmony", "visual", "hierarchy", "aligned", "grid"
    ]
    
    integration_score = 0.0
    max_score = len(integration_terms)
    
    # Count the number of integration terms mentioned
    for term in integration_terms:
        if term in generated_slide:
            integration_score += 1.0
    
    # Check if the description mentions all available elements
    elements_mentioned = 0
    max_elements = 0
    
    if slide_data.get("image_specs"):
        max_elements += 1
        if any(term in generated_slide for term in ["image", "picture", "photo", "graphic"]):
            elements_mentioned += 1
    
    if slide_data.get("diagram_specs"):
        max_elements += 1
        if any(term in generated_slide for term in ["diagram", "chart", "flowchart", "mindmap"]):
            elements_mentioned += 1
    
    if slide_data.get("data_viz_specs"):
        max_elements += 1
        if any(term in generated_slide for term in ["data", "visualization", "graph", "chart"]):
            elements_mentioned += 1
    
    # Calculate element integration score
    element_integration_score = elements_mentioned / max_elements if max_elements > 0 else 0.5
    
    # Combine scores (normalized to 0-1)
    combined_score = (integration_score / max_score * 0.6) + (element_integration_score * 0.4)
    
    return combined_score


def evaluate_slide_relevance(slide_data: Dict[str, Any]) -> float:
    """
    Evaluate how relevant the generated slide is to the original content.
    
    Args:
        slide_data: The slide data to evaluate
        
    Returns:
        A score between 0 and 1 indicating relevance
    """
    slide_content = slide_data.get("slide_content", {})
    generated_slide = slide_data.get("generated_slide", "").lower()
    
    # Extract key content
    title = slide_content.get("title", "").lower()
    content = slide_content.get("content", "").lower()
    
    # No content to evaluate
    if not title and not content:
        return 0.5  # Neutral score
    
    # Calculate overlap between original content and generated slide
    # This is a simple approach - could be improved with semantic similarity
    
    # Get words from original content
    original_words = set((title + " " + content).split())
    
    # Get words from generated slide
    generated_words = set(generated_slide.split())
    
    # Calculate word overlap
    if not original_words or not generated_words:
        return 0.5  # Neutral score
    
    # Jaccard similarity
    overlap = len(original_words.intersection(generated_words))
    union = len(original_words.union(generated_words))
    
    # Calculate score (adjusted to give reasonable results)
    relevance_score = min(1.0, overlap / (union * 0.3) if union > 0 else 0.5)
    
    return relevance_score


def evaluate_slide_quality(slide_data: Dict[str, Any]) -> float:
    """
    Evaluate the overall quality of the generated slide.
    
    Args:
        slide_data: The slide data to evaluate
        
    Returns:
        A score between 0 and 1 indicating quality
    """
    # This is a subjective measure that combines various factors
    
    generated_slide = slide_data.get("generated_slide", "")
    slide_type = slide_data.get("slide_type", "standard")
    
    # Basic length check - too short descriptions are likely incomplete
    if len(generated_slide) < 100:
        return 0.3
    
    # Check for quality indicators in the description
    quality_terms = [
        "visual", "clear", "readable", "engaging", "professional", "balanced",
        "hierarchy", "focus", "attention", "effective", "clean", "elegant"
    ]
    
    quality_score = 0.0
    for term in quality_terms:
        if term in generated_slide.lower():
            quality_score += 0.1
    
    # Cap at 1.0
    quality_score = min(1.0, quality_score)
    
    # Adjust based on slide type
    if slide_type == "title" and "first impression" in generated_slide.lower():
        quality_score += 0.1
    
    if slide_type == "data_viz" and any(term in generated_slide.lower() for term in 
                                     ["insight", "trends", "patterns", "comparison"]):
        quality_score += 0.1
    
    # Cap at 1.0 again after adjustments
    quality_score = min(1.0, quality_score)
    
    return quality_score


def evaluate_slide_generator_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple slide generator agent responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    # Filter out error responses
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid slide generator responses to evaluate")
        return None
    
    # If only one valid response, return it
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    # Evaluate each response
    scored_responses = []
    
    for response in valid_responses:
        slide_data = response.data
        
        # Calculate scores for different criteria
        completeness = evaluate_slide_completeness(slide_data)
        integration = evaluate_slide_integration(slide_data)
        relevance = evaluate_slide_relevance(slide_data)
        quality = evaluate_slide_quality(slide_data)
        
        # Calculate weighted total score
        # Weights can be adjusted based on importance
        total_score = (
            completeness * 0.3 + 
            integration * 0.3 + 
            relevance * 0.2 + 
            quality * 0.2
        )
        
        # Add to scored responses
        scored_responses.append((response, total_score))
        
        # Log evaluation
        logger.info(f"Slide evaluation - Completeness: {completeness:.2f}, "
                    f"Integration: {integration:.2f}, Relevance: {relevance:.2f}, "
                    f"Quality: {quality:.2f}, Total: {total_score:.2f}")
    
    # Sort by score (descending) and get the best response
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    # Log the selected response
    logger.info(f"Selected slide with score {best_score:.2f}")
    
    return best_response