from llm.askAI import callGPT
import json
import re

SYSTEM_ENTITY = {
    "role": "system",
    "content": (
        "You are a medical entity extraction system. "
        "Extract structured medical entities from the provided text. "
        "Respond ONLY with a valid JSON object — no explanation, no markdown, no backticks. "
        "Use this exact structure:\n"
        "{\n"
        '  "conditions": [{"name": str, "severity": "mild|moderate|severe|unknown"}],\n'
        '  "symptoms": [{"name": str, "severity": "mild|moderate|severe|unknown"}],\n'
        '  "medications": [{"name": str, "dosage": str or null}],\n'
        '  "lab_values": [{"name": str, "value": str, "status": "normal|abnormal|critical|unknown"}],\n'
        '  "recommendations": [str]\n'
        "}"
    )
}


def extract_entities(text: str) -> dict | None:
    """
    Extract medical entities from a text using GPT.
    Returns a dict with conditions, symptoms, medications, lab_values, recommendations.
    Returns None if extraction fails.
    """
    if not text or len(text.strip()) < 50:
        return None

    try:
        conversation = [
            SYSTEM_ENTITY,
            {"role": "user", "content": f"Extract medical entities from this text:\n\n{text[:3000]}"}
        ]
        raw = callGPT(conversation, 0.0)
        cleaned = re.sub(r"```json|```", "", raw).strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"Entity extraction failed (non-fatal): {e}")
        return None