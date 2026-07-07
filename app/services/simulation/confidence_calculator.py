from typing import List, Dict, Any
from statistics import pstdev

def calculate_confidence(scenarios: List[Dict[str, Any]]) -> float:
    """
    Calculates a deterministic confidence score (0.0 to 1.0) based on the variance 
    between the provided scenarios. High variance -> lower confidence.
    Never uses an LLM to guess.
    """
    if not scenarios:
        return 0.5
    
    # Small data penalty
    if len(scenarios) < 3:
        return 0.50
        
    profits = [s.get("profit", 0) for s in scenarios]
    revenues = [s.get("revenue", 0) for s in scenarios]
    max_p = max(profits)
    min_p = min(profits)
    
    if max_p == 0 and min_p == 0:
        return 0.85
        
    spread = abs(max_p - min_p)
    avg = sum(profits) / len(profits)
    
    avg = max(abs(avg), 1.0)
        
    volatility = spread / avg

    # Profit stability using standard deviation
    std_dev = pstdev(profits) if len(profits) > 1 else 0
    stability_penalty = min(std_dev / avg, 0.30)
    
    # Base confidence is 90% (assuming good MVP data completeness).
    # Subtract volatility penalty.
    penalty = min(
        volatility * 0.15 +
        stability_penalty * 0.15,
        0.40
    )
    
    # Small reward if revenues are consistent
    revenue_spread = (max(revenues) - min(revenues)) if revenues else 0

    if revenue_spread < 500:
        confidence_bonus = 0.03
    else:
        confidence_bonus = 0

    confidence = 0.90 - penalty + confidence_bonus
    confidence = max(0.10, min(confidence, 0.98))
    return round(confidence, 2)
