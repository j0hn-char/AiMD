import os
import re
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .prompts import RESPONSE_COMPARISON_PROMPT, FINALIZE_RESPONSE_PROMPT

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def callGPT(messages: list, temperature: float) -> str:
    response = await client.chat.completions.create(
        model="gpt-5.1",
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def _parse_json(raw: str) -> dict | None:
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

async def responseComparison(conversation: list) -> dict:
    MAX_ATTEMPTS = 2

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Both diagnosis calls run truly in parallel
        response1, response2 = await asyncio.gather(
            callGPT(conversation, 0.2),
            callGPT(conversation, 0.6),
        )

        comparison_content = (
            RESPONSE_COMPARISON_PROMPT
            .replace("{RESPONSE_1}", response1)
            .replace("{RESPONSE_2}", response2)
        )
        comparison_messages = [{"role": "user", "content": comparison_content}]

        # Retry JSON parse up to 3 times, but reuse the same prompt
        result = None
        for _ in range(3):
            raw = await callGPT(comparison_messages, 0.2)
            result = _parse_json(raw)
            if result:
                break

        if result and result.get("consistent"):
            return result

        print(f"[Attempt {attempt}] Diagnoses inconsistent, retrying...")

    return {"error": "Diagnoses remained inconsistent after maximum attempts"}

async def finalizeResponse(response: str, topPapers: list) -> dict:
    papers_text = "\n".join(
        f"[{p['citation']}]\n\n" + "\n\n".join(p['text'])
        for p in topPapers
    )

    prompt = (
        FINALIZE_RESPONSE_PROMPT
        .replace("{DIAGNOSIS}", response)
        .replace("{PAPERS}", papers_text)
    )

    raw = await callGPT([{"role": "user", "content": prompt}], 0.2)
    result = _parse_json(raw)
    if result is None:
        raise ValueError(f"Failed to parse finalizeResponse JSON: {raw!r}")
    return result