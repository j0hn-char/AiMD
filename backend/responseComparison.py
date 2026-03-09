from backend.chatbotCall import chatbotGPT, chatbotClaude
import json
import re
from concurrent.futures import ThreadPoolExecutor


def responseComparison(conversation):
    MAX_ATTEMPTS=4
    prompt = (
        "You will be given two medical diagnoses produced by AI chatbots. "
        "Your task is to analyze their consistency — that is, whether they convey "
        "roughly the same medical findings, conclusions, and recommendations.\n\n"
        "Diagnosis 1: {DIAGNOSIS_1}\n"
        "Diagnosis 2: {DIAGNOSIS_2}\n\n"
        "Compare the two diagnoses and respond only with a valid JSON object in the following format:\n\n"
        "```json\n"
        "{\n"
        '  "consistent": <true if the two diagnoses convey roughly the same findings and conclusions, false otherwise>,\n'
        '  "diagnosis": "<a single, coherent combined diagnosis that merges the key points of both texts into one unified summary>"\n'
        "}\n"
        "```\n\n"
        "Rules:\n"
        "* Do not include any text outside the JSON object.\n"
        "* Set `consistent` to `true` only if the two diagnoses are in substantial agreement "
        "(same condition, similar severity, compatible recommendations).\n"
        "* The `combined_diagnosis` should be a clean, professional medical summary that integrates "
        "both texts without contradictions. If they are inconsistent, do not produce the combined text."
        "Respond ONLY with a raw JSON object. Do NOT wrap it in markdown code blocks or backticks."
        )
    for attempt in range(1, MAX_ATTEMPTS+1):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futureGPT    = executor.submit(chatbotGPT, conversation)
            futureClaude = executor.submit(chatbotClaude, conversation)
            responseGPT    = futureGPT.result()
            responseClaude = futureClaude.result()
        
    
        comparisonPrompt = prompt.replace("{DIAGNOSIS_1}", responseGPT).replace("{DIAGNOSIS_2}", responseClaude)
        rawResponse = chatbotClaude(comparisonPrompt)
        cleaned = re.sub(r"```json|```", "", rawResponse).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[Attempt {attempt}] JSON parse error: {e}\nRaw: {rawResponse}")
            if attempt >= MAX_ATTEMPTS:
                return {"error": "Failed to parse comparison response after max attempts"}
            continue

        if result.get("consistent"):
            return result

        print(f"[Attempt {attempt}] Diagnoses inconsistent, retrying...")

    return {"error": "Diagnoses remained inconsistent after maximum attempts"}