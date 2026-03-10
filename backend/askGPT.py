import os
import openai
import json
import re
from concurrent.futures import ThreadPoolExecutor

openAIclient = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))      # Use environment variable for security

def callGPT(prompt, numOfResponses):
    response = openAIclient.chat.completions.create(
        model="gpt-5.1",       #(analoga to key)
        messages=prompt,
        n=numOfResponses
    )
    if numOfResponses == 1:
        return response.choices[0].message.content.strip()
    elif numOfResponses == 2:
        return (
            response.choices[0].message.content.strip(),
            response.choices[1].message.content.strip()
        )


def responseComparison(conversation):
    MAX_ATTEMPTS=3
    prompt = (
        "You will be given two medical diagnoses produced by AI chatbots. "
        "Your task is to analyze their consistency — that is, whether they convey "
        "roughly the same medical findings, conclusions, and recommendations.\n\n"
        "Diagnosis 1: {DIAGNOSIS_1}\n"
        "Diagnosis 2: {DIAGNOSIS_2}\n\n"
        "Compare the two diagnoses and respond only with a valid JSON object in the following format:\n\n"
        "{\n"
        '  "consistent": <true if the two diagnoses convey roughly the same findings and conclusions, false otherwise>,\n'
        '  "combined_diagnosis": "<a single, coherent combined diagnosis that merges the key points of both texts into one unified summary>",\n'
        '  "pubmed_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", ...]\n'
        "}\n\n"
        "Rules:\n"
        "* Do not include any text outside the JSON object.\n"
        "* Do NOT wrap the response in markdown code blocks or backticks.\n"
        "* Set `consistent` to `true` only if the two diagnoses are in substantial agreement "
        "(same condition, similar severity, compatible recommendations).\n"
        "* The `combined_diagnosis` should be a clean, professional medical summary that integrates "
        "both texts without contradictions. If they are inconsistent, do not produce the combined text.\n"
        "* The `pubmed_keywords` field must contain 5 to 10 precise medical search terms in English (MeSH terms preferred) "
        "that, when searched on PubMed, would return peer-reviewed papers supporting or elaborating on the diagnosis. "
        "Include condition names, relevant pathogens, symptoms, and diagnostic methods where appropriate."
    )
    for attempt in range(1, MAX_ATTEMPTS+1):
        response1, response2 = callGPT(conversation, 2)
    
        comparisonPrompt = prompt.replace("{DIAGNOSIS_1}", response1).replace("{DIAGNOSIS_2}", response2)
        #rawResponse= callGPT([{"role": "user", "content": comparisonPrompt}], 1)

        for parse_attempt in range(3):
            rawResponse = callGPT([{"role": "user", "content": comparisonPrompt}], 1)
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
    
    #h ylopoihsh den einai diskolh, tha ejartitei apo to output toy get_top_papers

    return response