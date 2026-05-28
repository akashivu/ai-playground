from openai import OpenAI
from dotenv import load_dotenv
from prompts.chat_prompts import SYSTEM_PROMPT
from prompts.sentiment_prompt import SENTIMENT_PROMPT
import os

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

def generate_response(messages : str):
    
    formatted_messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content":msg.content
        })
    response = client.chat.completions.create(
        model = "gpt-4.1-mini",

        messages=formatted_messages,
        temperature=0.7,
        

    )

    return response.choices[0].message.content

