import os
import json
from typing import Dict, Any, List
from google import genai
from google.genai import types

def explain_decision(question: str, scenarios: List[Dict[str, Any]], graph_context: Dict[str, Any]) -> Dict[str, str]:
    """
    Uses Gemini to narrate the finalized deterministic scenarios.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_explanation()

    client = genai.Client(api_key=api_key)
    
    system_instruction = (
        "You will be given final, already-computed numbers for three scenarios (Optimistic, Likely, Pessimistic) "
        "and a graph context. Explain and narrate them in plain English. Do not calculate, estimate, or alter any number. "
        "If a number is missing, say so — do not invent one. Focus on narrating the causal chain, providing a recommendation, "
        "and listing evidence/assumptions/risks based only on the data provided."
    )
    
    prompt = f"""
    Decision Question: {question}
    
    Computed Scenarios (JSON):
    {json.dumps(scenarios, indent=2)}
    
    Graph Context / Affected Nodes (JSON):
    {json.dumps(graph_context, indent=2)}
    
    Please provide your response in the following JSON format strictly:
    {{
        "causal_explanation": "A paragraph explaining the causal chain of what will happen.",
        "recommendation": "A short, plain-English recommendation on whether to proceed.",
        "evidence_and_risks": "A list of bullet points detailing the risks and assumptions based on the provided metrics."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"LLM Explanation failed: {e}")
        return _fallback_explanation()

def _fallback_explanation() -> Dict[str, str]:
    return {
        "causal_explanation": "The simulation results indicate a varying degree of impact based on demand and operational constraints. (Fallback Explanation)",
        "recommendation": "Review the deterministic scenario metrics to make an informed decision.",
        "evidence_and_risks": "Risk level varies across scenarios. Monitor key metrics closely."
    }
