from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

def generate_response(user_message : str):

    response = client.chat.completions.create(
        model = "gpt-4.1-mini",

        messages=[
            {
                "role": "system",
                "content" : "you are helpful ai assistant"
            },
            {
                "role": "user",
                "content": "user_message"
            }
        ],
        temperature=0.7

    )

    return response.choices[0].message.content