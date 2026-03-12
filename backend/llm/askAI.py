import os
import re
import json
import openai
#from typer import prompt
from dotenv import load_dotenv
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

openAIclient = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))      
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))        # Use environment variable for security

def callGPT(prompt):
    response = openAIclient.chat.completions.create(
        model="gpt-5.1",       #(analoga to key)
        messages=prompt
    )
    return response.choices[0].message.content.strip()
   

def chatbotGemini(conversation: str) -> str:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are an experienced medical assistant. "
            "Analyze the provided medical information carefully and provide "
            "a clear, professional diagnosis with recommendations."
        )
    )
    
    response = model.generate_content(conversation)
    return response.text

def responseComparison(conversation):
    MAX_ATTEMPTS=2
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
       with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(callGPT, conversation)
        f2 = executor.submit(chatbotGemini, conversation)
        response1 = f1.result()
        response2 = f2.result()

        comparisonPrompt = prompt.replace("{DIAGNOSIS_1}", response1).replace("{DIAGNOSIS_2}", response2)
        #rawResponse= callGPT([{"role": "user", "content": comparisonPrompt}])

        result = {
            "consistent": False,
            "combined_diagnosis": "",
            "pubmed_keywords":[]
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
        papers_text += f"[{paper['citation']}] {paper['text']}\n\n"
    
    prompt= """You will be given a medical diagnosis and a set of excerpts from scientific papers, each accompanied by its citation.

    Diagnosis:
    {DIAGNOSIS}

    Paper Excerpts:
    {PAPERS}
    (Each entry in PAPERS follows the format: [Citation] Excerpt text)

    Your task is to produce a JSON object with exactly two keys: "report" and "summary".

    ---

    "report" — A complete, well-structured medical report in Markdown format that:
    - Opens with a title (e.g., # Medical Report) and a table of contents
    - Is organized into clearly labeled sections with headings and subheadings, such as:
    ## 1. Overview
    ## 2. Clinical Findings
    ## 3. Supporting Evidence
    ### 3.1 ...
    ## 4. Discrepancies or Limitations (if any)
    ## 5. Conclusion
    - Presents the diagnosis as the central claim
    - Weaves in the provided paper excerpts to support, confirm, or elaborate on the diagnosis wherever relevant
    - Places the citation immediately after each use of a paper excerpt in inline format, e.g.: "...viral bronchitis is typically self-limiting (Smith et al., 2021)."
    - Only uses the provided excerpts — do not cite or invent any external sources
    - If a paper excerpt does not support the diagnosis, acknowledges the discrepancy briefly rather than forcing a false confirmation
    - Writes in a clear, clinical tone suitable for a formal medical report
    - Ends with a ## References section listing all cited sources

    "summary" — A concise 3–5 sentence plain-language summary of the report, suitable for display as a chatbot response to the patient or clinician. It should capture the key diagnosis, the main supporting evidence, and any notable caveats.

    ---

    Respond ONLY with a valid JSON object. Do not include any text, explanation, or markdown fences outside the JSON. The format must be exactly:
    {"report": "<full markdown report here>", "summary": "<short summary here>"}
    """.replace("{DIAGNOSIS}", response).replace("{PAPERS}", papers_text)
           
            
    final_response=callGPT([{"role": "user", "content": prompt}])
    return final_response