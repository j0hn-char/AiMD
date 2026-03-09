import os
import openai
import anthropic

#Sto pr;wto bhma to prompt tha einai ena string poy tha periexei olh thn yparxusa syzhthsh + to neo prompt
#morfhs 
# prompt = [
#   {"role": "user", "content": "Hello!"},
#    {"role": "assistant", "content": "Hi there!"}
#]

openAIclient = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))      # Use environment variable for security
ClaudeClient = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))        # Use environment variable for security

def chatbotGPT(prompt):
    response = openAIclient.chat.completions.create(
        model="gpt-3.5-turbo",       #(analoga to key)
        messages=prompt
    )
    return f"GPT: {response.choices[0].message.content.strip()}"

def chatbotClaude(prompt):
    response = ClaudeClient.messages.create(
         model="claude-3-sonnet-20240229",       #(analoga to key)
         max_tokens=1024,
         messages=prompt
     )
    bot_message = response.content[0].text.strip()
    return f"Claude: {bot_message}"  # Added strip for consistency