"""
Evaluation functions for the Slide Content Agent.
"""

import logging
from typing import Dict, Any, List

from libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)


def evaluate_content_clarity(slide_content: Dict[str, Any]) -> float:
    """
    Evaluate the clarity of slide content.
    
    Args:
        slide_content: The slide content to evaluate
        
    Returns:
        A score between 0 and 1 indicating clarity
    """
    score = 0.0
    max_score = 3.0
    
    # Check for clear title
    title = slide_content.get("title", "")
    if title:
        # Title should be concise but informative
        title_length = len(title)
        if 3 <= title_length <= 10:  # Very short
            score += 0.7
        elif 10 < title_length <= 70:  # Good length
            score += 1.0
        else:  # Too long
            score += 0.4
    
    # Check content length and structure
    content = slide_content.get("content", "")
    if content:
        # Content should be substantial but not overwhelming
        content_length = len(content)
        content_lines = content.count("\n") + 1
        
        # Ideal: 3-7 bullet points or 100-300 characters
        if (3 <= content_lines <= 7) or (100 <= content_length <= 300):
            score += 1.0
        elif (1 <= content_lines < 3) or (50 <= content_length < 100):
            score += 0.7  # Too brief
        elif (7 < content_lines <= 10) or (300 < content_length <= 500):
            score += 0.7  # Getting lengthy
        else:
            score += 0.3  # Either too short or too long
    
    # Check for speaker notes (helpful for clarity during presentation)
    if slide_content.get("notes"):
        score += 1.0
    
    # Normalize score to be between 0 and 1
    return score / max_score


def evaluate_content_relevance(slide_content: Dict[str, Any], section_info: Dict[str, Any]) -> float:
    """
    Evaluate how relevant the slide content is to its section.
    
    Args:
        slide_content: The slide content to evaluate
        section_info: Information about the section this slide belongs to
        
    Returns:
        A score between 0 and 1 indicating relevance
    """
    # If no section info is provided, can't evaluate relevance properly
    if not section_info:
        return 0.7  # Default moderate score
    
    title = slide_content.get("title", "").lower()
    content = slide_content.get("content", "").lower()
    
    section_title = section_info.get("title", "").lower()
    section_desc = section_info.get("description", "").lower()
    key_points = [point.lower() for point in section_info.get("key_points", [])]
    
    # If content is empty, low relevance
    if not title and not content:
        return 0.3
    
    # Check if slide title contains or relates to section title
    title_relevance = 0.0
    if section_title in title or any(word in title for word in section_title.split()):
        title_relevance = 1.0
    else:
        # Check for partial matches
        title_words = title.split()
        section_words = section_title.split()
        
        matches = sum(1 for word in title_words if any(word in s_word or s_word in word for s_word in section_words))
        if matches > 0:
            title_relevance = min(1.0, matches / len(section_words))
    
    # Check if content relates to section description and key points
    content_relevance = 0.0
    
    # Check against section description
    if section_desc and any(word in content for word in section_desc.split()):
        content_relevance += 0.5
    
    # Check against key points
    key_point_matches = sum(1 for point in key_points if any(word in content for word in point.split()))
    if key_points:
        content_relevance += min(0.5, key_point_matches / len(key_points))
    
    # Combined score with equal weighting
    relevance_score = (title_relevance + content_relevance) / 2
    
    return relevance_score


def evaluate_content_visual_support(slide_content: Dict[str, Any]) -> float:
    """
    Evaluate the visual support elements requested in the slide content.
    
    Args:
        slide_content: The slide content to evaluate
        
    Returns:
        A score between 0 and 1 indicating visual support quality
    """
    score = 0.0
    max_score = 3.0
    
    # Check for image specifications
    images_needed = slide_content.get("images_needed", [])
    if images_needed:
        # Having 1-2 images is usually good
        if 1 <= len(images_needed) <= 2:
            score += 1.0
        else:
            score += 0.5  # Too many or too few images
    
    # Check for diagram specifications
    diagrams_needed = slide_content.get("diagrams_needed", [])
    if diagrams_needed:
        # Having one diagram is usually good
        if len(diagrams_needed) == 1:
            score += 1.0
        else:
            score += 0.5  # Too many diagrams can be confusing
    
    # Check for data visualization specifications
    data_viz_needed = slide_content.get("data_viz_needed", [])
    if data_viz_needed:
        # Having one data visualization is usually good
        if len(data_viz_needed) == 1:
            score += 1.0
        else:
            score += 0.5  # Too many visualizations can be confusing
    
    # If no visual support is requested, give partial credit
    # Some slides don't need visuals, but many benefit from them
    if not images_needed and not diagrams_needed and not data_viz_needed:
        score += 0.5
    
    # Normalize score to be between 0 and 1
    return score / max_score


def evaluate_content_depth(slide_content: Dict[str, Any]) -> float:
    """
    Evaluate the depth and substance of the slide content.
    
    Args:
        slide_content: The slide content to evaluate
        
    Returns:
        A score between 0 and 1 indicating content depth
    """
    content = slide_content.get("content", "")
    
    # If content is empty, no depth
    if not content:
        return 0.0
    
    # Evaluate based on content length and structure
    content_length = len(content)
    
    # Count sentences (rough approximation)
    sentence_count = content.count(". ") + content.count("! ") + content.count("? ") + 1
    
    # Count bullet points
    bullet_count = content.count("\n- ") + content.count("\n* ") + content.count("\n• ")
    if content.startswith("- ") or content.startswith("* ") or content.startswith("• "):
        bullet_count += 1
    
    # Calculate depth score based on content characteristics
    depth_score = 0.0
    
    # Length-based evaluation
    if content_length < 50:
        depth_score += 0.2  # Very brief
    elif 50 <= content_length < 150:
        depth_score += 0.5  # Moderate depth
    elif 150 <= content_length < 300:
        depth_score += 0.8  # Good depth
    else:
        depth_score += 0.6  # Could be too verbose for a slide
    
    # Structure-based evaluation
    if bullet_count > 0:
        # Good bullet point count
        if 3 <= bullet_count <= 7:
            depth_score += 0.2
        else:
            depth_score += 0.1  # Too few or too many
    elif sentence_count > 1:
        # Good sentence structure
        if 2 <= sentence_count <= 5:
            depth_score += 0.2
        else:
            depth_score += 0.1  # Too few or too many
    
    # Cap at 1.0
    return min(1.0, depth_score)


def evaluate_slide_content_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple slide content agent responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    # Filter out error responses
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid slide content responses to evaluate")
        return None
    
    # If only one valid response, return it
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    # Evaluate each response
    scored_responses = []
    
    for response in valid_responses:
        slide_content = response.data
        metadata = response.metadata or {}
        
        # Get section info from metadata if available
        section_info = metadata.get("section_info", {})
        
        # Calculate scores for different criteria
        clarity = evaluate_content_clarity(slide_content)
        relevance = evaluate_content_relevance(slide_content, section_info)
        visual_support = evaluate_content_visual_support(slide_content)
        depth = evaluate_content_depth(slide_content)
        
        # Calculate weighted total score
        # Weights can be adjusted based on importance
        total_score = (
            clarity * 0.3 + 
            relevance * 0.3 + 
            visual_support * 0.2 + 
            depth * 0.2
        )
        
        # Add to scored responses
        scored_responses.append((response, total_score))
        
        # Log evaluation
        logger.info(f"Slide content evaluation - Clarity: {clarity:.2f}, "
                    f"Relevance: {relevance:.2f}, Visual Support: {visual_support:.2f}, "
                    f"Depth: {depth:.2f}, Total: {total_score:.2f}")
    
    # Sort by score (descending) and get the best response
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    # Log the selected response
    logger.info(f"Selected slide content with score {best_score:.2f}")
    
    return best_response