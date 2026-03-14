from file_processor import process_file
from llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from llm.generate_final_report import generate_pdf

conversation = []
files = []

conversation.append({"role": "system", "content": "You are a helpful and precise assistant for medical use."})

userMessage = "what is mediterranean anemia?" #Mhnhmata pou tha erxontai apo to frontend
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
    response = responseComparison(conversation)
    if "error" in response:
        print(f"Error: {response['error']}")
    elif response["consistent"]:  
        top_papers = get_top_papers(response)
        if not top_papers:
            print("No relevant papers found.")
        else:
            final_response = finalizeResponse(response["combined_diagnosis"], top_papers)
            generate_pdf(final_response["report"], "report.pdf")
            print(final_response["summary"])
            conversation.append({"role": "assistant", "content": final_response["summary"]})
    else:
        print("unable to get a consistent answer, error message sent to user")
else:
    short_conversation = conversation + [{
        "role": "user",
        "content": "Answer briefly and in a friendly, simple way. No technical jargon, no long explanations."
    }]
    small_response = callGPT(short_conversation, 0.2)
    print(small_response)
    conversation.append({"role": "assistant", "content": small_response})


