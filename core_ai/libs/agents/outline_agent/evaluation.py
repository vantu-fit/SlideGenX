"""
Evaluation functions for the Outline Agent.
"""

import logging
from typing import Dict, Any, List

from libs.core.agent_response import AgentResponse

logger = logging.getLogger(__name__)


def evaluate_outline_completeness(outline: Dict[str, Any]) -> float:
    """
    Evaluate the completeness of a presentation outline.
    
    Args:
        outline: The outline to evaluate
        
    Returns:
        A score between 0 and 1 indicating completeness
    """
    score = 0.0
    max_score = 4.0
    
    # Check for essential components
    if outline.get("title"):
        score += 1.0
    
    if outline.get("sections") and len(outline.get("sections", [])) > 0:
        score += 1.0
    
    if outline.get("target_audience"):
        score += 1.0
    
    if outline.get("overall_message"):
        score += 1.0
    
    # Normalize score to be between 0 and 1
    return score / max_score


def evaluate_outline_structure(outline: Dict[str, Any]) -> float:
    """
    Evaluate the structure of a presentation outline.
    
    Args:
        outline: The outline to evaluate
        
    Returns:
        A score between 0 and 1 indicating structure quality
    """
    sections = outline.get("sections", [])
    
    if not sections:
        return 0.0
    
    section_scores = []
    
    for section in sections:
        section_score = 0.0
        max_section_score = 3.0
        
        # Check for essential section components
        if section.get("title"):
            section_score += 1.0
        
        if section.get("description"):
            section_score += 1.0
        
        if section.get("key_points") and len(section.get("key_points", [])) > 0:
            section_score += 1.0
        
        # Add normalized section score
        section_scores.append(section_score / max_section_score)
    
    # Average the section scores
    return sum(section_scores) / len(section_scores) if section_scores else 0.0


def evaluate_outline_balance(outline: Dict[str, Any]) -> float:
    """
    Evaluate the balance of a presentation outline.
    
    Args:
        outline: The outline to evaluate
        
    Returns:
        A score between 0 and 1 indicating balance
    """
    sections = outline.get("sections", [])
    
    if not sections or len(sections) < 2:
        return 0.5  # Not enough sections to evaluate balance
    
    # Get estimated slides per section
    slides_per_section = [section.get("estimated_slides", 0) for section in sections]
    
    # Calculate coefficient of variation (standard deviation / mean)
    import statistics
    
    # Avoid division by zero
    if sum(slides_per_section) == 0:
        return 0.5
    
    try:
        mean = statistics.mean(slides_per_section)
        stdev = statistics.stdev(slides_per_section) if len(slides_per_section) > 1 else 0
        cv = stdev / mean if mean > 0 else 0
        
        # Convert to a score (lower CV means better balance)
        # CV of 0 is perfect balance, CV of 1 or more is poor balance
        balance_score = max(0, 1 - cv)
        
        return balance_score
    except:
        # Fallback if statistical functions fail
        return 0.5


def evaluate_outline_responses(responses: List[AgentResponse]) -> AgentResponse:
    """
    Evaluate multiple outline responses and select the best one.
    
    Args:
        responses: List of agent responses to evaluate
        
    Returns:
        The best response
    """
    # Filter out error responses
    valid_responses = [r for r in responses if r.status == "success"]
    
    if not valid_responses:
        logger.warning("No valid outline responses to evaluate")
        return None
    
    # If only one valid response, return it
    if len(valid_responses) == 1:
        return valid_responses[0]
    
    # Evaluate each response
    scored_responses = []
    
    for response in valid_responses:
        outline = response.data
        
        # Calculate scores
        completeness = evaluate_outline_completeness(outline)
        structure = evaluate_outline_structure(outline)
        balance = evaluate_outline_balance(outline)
        
        # Calculate weighted total score
        # Weights can be adjusted based on importance
        total_score = (completeness * 0.4) + (structure * 0.4) + (balance * 0.2)
        
        # Add to scored responses
        scored_responses.append((response, total_score))
        
        # Log evaluation
        logger.info(f"Outline evaluation - Completeness: {completeness:.2f}, "
                    f"Structure: {structure:.2f}, Balance: {balance:.2f}, "
                    f"Total: {total_score:.2f}")
    
    # Sort by score (descending) and get the best response
    scored_responses.sort(key=lambda x: x[1], reverse=True)
    best_response, best_score = scored_responses[0]
    
    # Log the selected response
    logger.info(f"Selected outline with score {best_score:.2f}")
    
    return best_response