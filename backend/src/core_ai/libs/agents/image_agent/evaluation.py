"""
Evaluation functions for the Image Agent.
"""

import logging
from typing import Dict, Any, List

from core_ai.libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)


def evaluate_image_specificity(image_spec: Dict[str, Any]) -> float:
    """
    Evaluate the specificity of an image specification.
    
    Args:
        image_spec: The image specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating specificity
    """
    score = 0.0
    max_score = 5.0
    
    # Check for detailed description
    description = image_spec.get("description", "")
    if description:
        # More detailed descriptions get higher scores
        desc_length = len(description)
        if desc_length > 200:
            score += 1.0
        elif desc_length > 100:
            score += 0.8
        elif desc_length > 50:
            score += 0.5
        else:
            score += 0.2
    
    # Check for style specification
    if image_spec.get("style"):
        score += 1.0
    
    # Check for size specification
    if image_spec.get("size"):
        score += 1.0
    
    # Check for placement specification
    if image_spec.get("placement"):
        score += 1.0
    
    # Check for search query
    search_query = image_spec.get("search_query", "")
    if search_query:
        # More specific search queries get higher scores
        query_terms = search_query.split()
        if len(query_terms) > 5:
            score += 1.0
        elif len(query_terms) > 3:
            score += 0.7
        else:
            score += 0.3
    
    # Normalize score to be between 0 and 1
    return score / max_score


def evaluate_image_relevance(image_spec: Dict[str, Any], slide_title: str, slide_content: str) -> float:
    """
    Evaluate the relevance of an image specification to the slide content.
    
    Args:
        image_spec: The image specification to evaluate
        slide_title: The title of the slide
        slide_content: The content of the slide
        
    Returns:
        A score between 0 and 1 indicating relevance
    """
    # This is a simplified evaluation that checks for keyword overlap
    # A more sophisticated approach would use semantic matching or embeddings
    
    # Extract keywords from slide title and content
    slide_text = (slide_title + " " + slide_content).lower()
    slide_words = set(slide_text.split())
    
    # Extract keywords from image description and search query
    image_text = (
        image_spec.get("description", "") + " " + 
        image_spec.get("search_query", "")
    ).lower()
    image_words = set(image_text.split())
    
    # Calculate overlap
    if not slide_words or not image_words:
        return 0.5  # Default if we can't calculate
    
    overlap = len(slide_words.intersection(image_words))
    max_possible = min(len(slide_words), len(image_words))
    
    if max_possible == 0:
        return 0.5  # Default if we can't calculate
    
    overlap_ratio = overlap / max_possible
    
    # Scale the ratio to account for common words
    # A perfect match would rarely have all words match
    adjusted_score = min(1.0, overlap_ratio * 2.5)
    
    return adjusted_score


def evaluate_image_visual_appeal(image_spec: Dict[str, Any]) -> float:
    """
    Evaluate the potential visual appeal of the specified image.
    
    Args:
        image_spec: The image specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating visual appeal
    """
    # This is a heuristic evaluation since we can't see the actual image
    
    style = image_spec.get("style", "").lower()
    description = image_spec.get("description", "").lower()
    
    # Preferred styles generally score higher
    preferred_styles = [
        "professional", "clean", "modern", "minimalist", 
        "high quality", "high resolution", "vibrant", "elegant"
    ]
    
    # Keywords that suggest visually appealing images
    appeal_keywords = [
        "colorful", "striking", "beautiful", "engaging", "eye-catching",
        "balanced", "composition", "visual", "aesthetic", "dramatic"
    ]
    
    # Calculate style score
    style_score = 0.0
    for preferred in preferred_styles:
        if preferred in style:
            style_score += 0.2
    style_score = min(1.0, style_score)
    
    # Calculate keyword score
    keyword_score = 0.0
    for keyword in appeal_keywords:
        if keyword in description:
            keyword_score += 0.1
    keyword_score = min(1.0, keyword_score)
    
    # Combined score with weights
    combined_score = (style_score * 0.6) + (keyword_score * 0.4)
    
    return combined_score


def evaluate_image_practicality(image_spec: Dict[str, Any]) -> float:
    """
    Evaluate how practical it would be to find and use the specified image.
    
    Args:
        image_spec: The image specification to evaluate
        
    Returns:
        A score between 0 and 1 indicating practicality
    """
    score = 0.0
    max_score = 3.0
    
    # Check if search query is reasonable (not too long or complex)
    search_query = image_spec.get("search_query", "")
    if search_query:
        words = search_query.split()
        if 2 <= len(words) <= 6:
            score += 1.0
        elif len(words) > 6:
            score += 0.5
        else:
            score += 0.3
    
    # Check if the image type is likely to be available
    description = image_spec.get("description", "").lower()
    common_image_types = [
        "person", "people", "building", "landscape", "chart", 
        "graph", "icon", "symbol", "office", "business", "technology"
    ]
    
    for image_type in common_image_types:
        if image_type in description:
            score += 1.0
            break
    
    # Check if placement is practical
    placement = image_spec.get("placement", "").lower()
    practical_placements = ["center", "right", "left", "background", "top", "bottom"]
    
    for pp in practical_placements:
        if pp in placement:
            score += 1.0
            break
    
    # Normalize score
    return score / max_score


def evaluate_image_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple image agent responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    # Filter out error responses
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid image responses to evaluate")
        return None
    
    # If only one valid response, return it
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    # Evaluate each response
    scored_responses = []
    
    for response in valid_responses:
        image_spec = response.data
        metadata = response.metadata or {}
        
        # Get slide information from metadata
        slide_title = metadata.get("slide_title", "")
        slide_content = metadata.get("slide_content", "")
        
        # Calculate scores for different criteria
        specificity = evaluate_image_specificity(image_spec)
        relevance = evaluate_image_relevance(image_spec, slide_title, slide_content)
        visual_appeal = evaluate_image_visual_appeal(image_spec)
        practicality = evaluate_image_practicality(image_spec)
        
        # Calculate weighted total score
        # Weights can be adjusted based on importance
        total_score = (
            specificity * 0.3 + 
            relevance * 0.4 + 
            visual_appeal * 0.2 + 
            practicality * 0.1
        )
        
        # Add to scored responses
        scored_responses.append((response, total_score))
        
        # Log evaluation
        logger.info(f"Image evaluation - Specificity: {specificity:.2f}, "
                    f"Relevance: {relevance:.2f}, Visual Appeal: {visual_appeal:.2f}, "
                    f"Practicality: {practicality:.2f}, Total: {total_score:.2f}")
    
    # Sort by score (descending) and get the best response
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    # Log the selected response
    logger.info(f"Selected image spec with score {best_score:.2f}")
    
    return best_response