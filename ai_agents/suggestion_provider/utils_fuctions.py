import json
import re

def classify_intent(user_input: str) -> str:
    lowered = user_input.lower()
    if any(greet in lowered for greet in ["hello", "hi", "hey", "yo", "good morning", "good evening"]):
        return "greeting"
    if any(thank in lowered for thank in ["thank you", "thanks", "appreciate"]):
        return "gratitude"
    if any(bye in lowered for bye in ["bye", "goodbye", "see you"]):
        return "farewell"
    if len(lowered.split()) <= 3:
        return "short"
    return "unknown"

def parse_llm_response(response: str):
    if not response.strip():
        return []

    try:
        parsed = json.loads(response)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        pass

    # Fallback: extract multiple JSON objects
    objects = re.findall(r'\{.*?\\}', response, re.DOTALL)
    result = []
    for obj in objects:
        try:
            result.append(json.loads(obj))
        except json.JSONDecodeError:
            continue
    return result