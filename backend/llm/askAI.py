import os
import re
import json
import anthropic
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from .prompts import RESPONSE_COMPARISON_PROMPT, FINALIZE_RESPONSE_PROMPT


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

ClaudeClient = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def chatbotClaude(prompt, temperature, max_tokens=1024):
    system_content = next(
        (m["content"] for m in prompt if m["role"] == "system"),
        None
    )
    messages = [
        m for m in prompt
        if m["role"] != "system" and (
            (isinstance(m.get("content"), str) and m["content"].strip()) or
            isinstance(m.get("content"), list)
        )
    ]

    response = ClaudeClient.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=[{"type": "text", "text": system_content}] if system_content else [],
        messages=messages,
        temperature=temperature
    )
    return response.content[0].text.strip()


def responseComparison(conversation):
    prompt = RESPONSE_COMPARISON_PROMPT

    # Τα 2 Claude calls τρέχουν παράλληλα
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(chatbotClaude, conversation, 0.2)
        f2 = executor.submit(chatbotClaude, conversation, 0.6)
        response1 = f1.result()
        response2 = f2.result()

    comparisonPrompt = (
        prompt
        .replace("{RESPONSE_1}", response1)
        .replace("{RESPONSE_2}", response2)
    )

    result = {
        "consistent": False,
        "combined_diagnosis": "",
        "pubmed_keywords": []
    }

    # Έως 2 προσπάθειες JSON parse
    for _ in range(2):
        rawResponse = chatbotClaude([{"role": "user", "content": comparisonPrompt}], 0.2)
        cleaned = re.sub(r"```json|```", "", rawResponse).strip()
        try:
            result = json.loads(cleaned)
            break
        except json.JSONDecodeError:
            continue

    # Επιστρέφουμε πάντα αποτέλεσμα — ακόμα και αν δεν είναι consistent ή άδειο
    if result.get("combined_diagnosis"):
        if not result.get("consistent"):
            print("[WARN] Responses inconsistent, returning best available result.")
        return result

    return {"error": "Diagnoses remained inconsistent after maximum attempts"}


def finalizeResponse(response, topPapers):
    papers_text = ""
    for paper in topPapers:
        chunks = "\n\n".join(paper["text"])
        papers_text += f"[{paper['citation']}]\n\n{chunks}\n\n"

    if not papers_text:
        papers_text = "No supporting papers were available for this analysis."

    prompt = (
        FINALIZE_RESPONSE_PROMPT
        .replace("{DIAGNOSIS}", response)
        .replace("{PAPERS}", papers_text)
    )

    # Χρησιμοποιούμε 8192 tokens για να χωράει ολόκληρο το report + summary σε JSON
    raw = chatbotClaude([{"role": "user", "content": prompt}], 0.2, max_tokens=8192)
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[ERROR] finalizeResponse JSON parse failed. Raw (first 500 chars): {raw[:500]}")
        return {"error": "Failed to parse finalized response"}