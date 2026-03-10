import os
import openai
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from typer import prompt
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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

        result = {
            "consistent": False,
            "combined_diagnosis": "",
            "pubmed_keywords":[]
        }
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
    
    papers_text = ""
    for paper in topPapers:
        papers_text += f"[{paper['citation']}] {paper['text']}\n\n"
    
    prompt="""You will be given a medical diagnosis and a set of excerpts from scientific papers, each accompanied by its citation.
            Diagnosis:
            {DIAGNOSIS}
            Paper Excerpts:
            {PAPERS}
            (Each entry in PAPERS follows the format: [Citation] Excerpt text)
            Your task is to write a cohesive, professional medical text that:

            Presents the diagnosis as the central claim.
            Weaves in the provided paper excerpts to support, confirm, or elaborate on the diagnosis wherever relevant.
            Places the citation immediately after each use of a paper excerpt, in inline format, e.g.: "...viral bronchitis is typically self-limiting (Smith et al., 2021)."
            Only uses the provided excerpts — do not cite or invent any external sources.
            If a paper excerpt does not support the diagnosis, acknowledge the discrepancy briefly rather than forcing a false confirmation.
            Writes in a clear, clinical tone suitable for a medical report.

            Respond only with the final text. Do not include any preamble, explanation, or commentary outside the medical report itself.
        """.replace("{DIAGNOSIS}", response).replace("{PAPERS}", papers_text)
           
            
    final_response=callGPT([{"role": "user", "content": prompt}], 1)
    return final_response