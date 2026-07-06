from typing import List, Dict, Any

def calculate_confidence(scenarios: List[Dict[str, Any]]) -> float:
    """
    Calculates a deterministic confidence score (0.0 to 1.0) based on the variance 
    between the provided scenarios. High variance -> lower confidence.
    Never uses an LLM to guess.
    """
    if not scenarios:
        return 0.5
        
    profits = [s.get("profit", 0) for s in scenarios]
    max_p = max(profits)
    min_p = min(profits)
    
    if max_p == 0 and min_p == 0:
        return 0.85
        
    spread = abs(max_p - min_p)
    avg = sum(profits) / len(profits)
    
    if avg == 0:
        avg = 1.0
        
    volatility = spread / abs(avg)
    
    # Base confidence is 90% (assuming good MVP data completeness).
    # Subtract volatility penalty.
    penalty = min(volatility * 0.2, 0.4)
    
    confidence = 0.90 - penalty
    return round(max(0.1, confidence), 2)
