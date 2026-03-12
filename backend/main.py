from AiMD.backend.file_processor import process_file
from backend.llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from llm.generate_final_report import generate_pdf

conversation = []
files = []

conversation.append({"role": "system", "content": "You are a helpful and precise assistant for medical use."})

userMessage = "" #Mhnhmata pou tha erxontai apo to frontend
for file in files: #Ta arxeia pou tha erxontai apo to frontend
    file_response = process_file(file["contents"], file["filename"])
    if file_response["type"] == "error":
        conversation.append({"role": "assistant", "content": file_response["data"]})
        print("unable to process file, error message sent to user")
    else:
        conversation.append({"role": "user", "content": f"Processed file: {file['filename']} - Type: {file_response['type']}"})

conversation.append({"role": "user", "content": userMessage})

switchIsOn=True #O diakoptis poy kathorizei to epipedo tis analysis, erxete apo frontent

if switchIsOn: 
    response=responseComparison(conversation)
    if(response["consistent"]):  
        top_papers=get_top_papers(response)
        final_response=finalizeResponse(response["combined_diagnosis"], top_papers)
        generate_pdf(final_response["report"], "report.pdf")
    else:
        #error message   
        print("unable to get a consistant answer, error message sent to user") 
else:
    response=callGPT(conversation)

conversation.append({"role": "assistant", "content": response})

