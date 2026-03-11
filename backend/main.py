from AiMD.backend.llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers

conversation = []

conversation.append({"role": "system", "content": "You are a helpful and precise assistant for medical use."})

userMessage = "" #Mhnhmata pou tha erxontai apo to frontend
conversation.append({"role": "user", "content": userMessage})

switchIsOn=True #O diakoptis poy kathorizei to epipedo tis analysis, erxete apo frontent

if switchIsOn: 
    response=responseComparison(conversation)
    if(response["consistent"]):  
        top_papers=get_top_papers(response)
        response=finalizeResponse(response["combined_diagnosis"], top_papers)
    else:
        #error message   
        print("error") 
else:
    response=callGPT(conversation)

conversation.append({"role": "assistant", "content": response})

