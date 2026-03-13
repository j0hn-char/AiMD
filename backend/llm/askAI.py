import os
import re
import json
import openai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from .prompts import RESPONSE_COMPARISON_PROMPT, FINALIZE_RESPONSE_PROMPT


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
openAIclient = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))      # Use environment variable for security

def callGPT(prompt, temperature):
    response = openAIclient.chat.completions.create(
        model="gpt-5.1",       #(analoga to key)
        messages=prompt,
        temperature=temperature,      # Lower temperature for more deterministic responses
    )
    
    return response.choices[0].message.content.strip()
  


def responseComparison(conversation):
    MAX_ATTEMPTS = 2
    prompt = RESPONSE_COMPARISON_PROMPT

    for attempt in range(1, MAX_ATTEMPTS + 1):
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(callGPT, conversation, 0.2)
            f2 = executor.submit(callGPT, conversation, 0.6)
            response1 = f1.result()
            response2 = f2.result()

        comparisonPrompt = prompt.replace("{DIAGNOSIS_1}", response1).replace("{DIAGNOSIS_2}", response2)

        result = {
            "consistent": False,
            "combined_diagnosis": "",
            "pubmed_keywords": []
        }

        for parse_attempt in range(3):
            rawResponse = callGPT([{"role": "user", "content": comparisonPrompt}], 0.2)
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

    final_response = callGPT([{"role": "user", "content": prompt}], 0.2)
    return final_response