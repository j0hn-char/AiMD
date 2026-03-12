import os
import re
import json
import openai
from dotenv import load_dotenv
import google.generativeai as genai
from .prompts import RESPONSE_COMPARISON_PROMPT, FINALIZE_RESPONSE_PROMPT
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
    prompt =RESPONSE_COMPARISON_PROMPT
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
    
    prompt=FINALIZE_RESPONSE_PROMPT.replace("{DIAGNOSIS}", response).replace("{PAPERS}", papers_text)
           
            
    final_response=callGPT([{"role": "user", "content": prompt}])
    return final_response