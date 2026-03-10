from backend.llm.askGPT import callGPT, responseComparison, finalizeResponse

conversation = []

conversation.append({"role": "system", "content": "You are a helpful and precise assistant for medical use."})

userMessage = "" #Mhnhmata pou tha erxontai apo to frontend
conversation.append({"role": "user", "content": userMessage})

switchIsOn=True #O diakoptis poy kathorizei to epipedo tis analysis, erxete apo frontent

if(switchIsOn): 
    response=responseComparison(conversation)
    #if gia consistancy 
        #top_papers=get_top_papers(response["pubmed_keywords"])
             #to pernei etoimo lina
        #get_relevant_chunks(response["content"],top_papers)
        #response=finalizeResponse(response, topPapers)
else:
    response=callGPT(conversation)

conversation.append({"role": "assistant", "content": response})

