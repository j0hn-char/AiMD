from backend.askGPT import callGPT, responseComparison, finalizeResponse

conversation = []

conversation.append({"role": "system", "content": "You are a helpful and precise assistant for medical use."})

userMessage = "" #Mhnhmata pou tha erxontai apo to frontend
conversation.append({"role": "user", "content": userMessage})

switchIsOn=True #O diakoptis poy kathorizei to epipedo tis analysis, erxete apo frontent

if(switchIsOn): 
    response=responseComparison(conversation)
    #topPapers=get_top_papers(response["pubmed_keywords"])
    #response=finalizeResponse(response, topPapers)
else:
    response=callGPT(conversation)

conversation.append({"role": "assistant", "content": response})

