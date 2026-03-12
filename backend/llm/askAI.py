import os
import re
import json
import openai
from dotenv import load_dotenv
from google import genai
from .prompts import RESPONSE_COMPARISON_PROMPT, FINALIZE_RESPONSE_PROMPT
from concurrent.futures import ThreadPoolExecutor

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

openAIclient = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def callGPT(prompt):
    response = openAIclient.chat.completions.create(
        model="gpt-5.1",
        messages=prompt
    )
    return response.choices[0].message.content.strip()


def chatbotGemini(conversation: list) -> str:
    system_instruction = ""
    for msg in conversation:
        if msg["role"] == "system":
            system_instruction = msg["content"]
            break

    gemini_contents = []
    for msg in conversation:
        if msg["role"] == "system":
            continue
        role = "user" if msg["role"] == "user" else "model"
        content = msg["content"]

        if isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    parts.append(genai.types.Part(text=part["text"]))
                elif part.get("type") == "image_url":
                    data_url = part["image_url"]["url"]
                    media_type, b64data = data_url.split(";base64,")
                    media_type = media_type.replace("data:", "")
                    parts.append(genai.types.Part(
                        inline_data=genai.types.Blob(
                            mime_type=media_type,
                            data=b64data
                        )
                    ))
            gemini_contents.append(genai.types.Content(role=role, parts=parts))
        else:
            gemini_contents.append(genai.types.Content(
                role=role,
                parts=[genai.types.Part(text=content)]
            ))

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=gemini_contents,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text


def responseComparison(conversation):
    MAX_ATTEMPTS = 2
    prompt = RESPONSE_COMPARISON_PROMPT

    for attempt in range(1, MAX_ATTEMPTS + 1):
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(callGPT, conversation)
            f2 = executor.submit(chatbotGemini, conversation)
            response1 = f1.result()
            response2 = f2.result()

        comparisonPrompt = prompt.replace("{DIAGNOSIS_1}", response1).replace("{DIAGNOSIS_2}", response2)

        result = {
            "consistent": False,
            "combined_diagnosis": "",
            "pubmed_keywords": []
        }

        for parse_attempt in range(3):
            rawResponse = callGPT([{"role": "user", "content": comparisonPrompt}])
            cleaned = re.sub(r"```json|```", "", rawResponse).strip()
            try:
                result = json.loads(cleaned)
                break
            except json.JSONDecodeError:
                continue

        if result.get("consistent"):
            return result

        print(f"[Attempt {attempt}] Diagnoses inconsistent, retrying...")

    return {"error": "Diagnoses remained inconsistent after maximum attempts"}


def finalizeResponse(response, topPapers):
    papers_text = ""
    for paper in topPapers:
        papers_text += f"[{paper['citation']}] {' '.join(paper['text'])}\n\n"

    prompt = FINALIZE_RESPONSE_PROMPT.replace("{DIAGNOSIS}", response).replace("{PAPERS}", papers_text)

    final_response = callGPT([{"role": "user", "content": prompt}])
    return final_response