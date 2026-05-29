from openai import AsyncOpenAI
from dotenv import load_dotenv
from prompts.chat_prompts import SYSTEM_PROMPT
from prompts.sentiment_prompt import SENTIMENT_PROMPT
from utils.logger import logger
import os

load_dotenv()

client = AsyncOpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

async def generate_response(messages : str):
    
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
    
    logger.info("generating AI response")
    
    response = await client.chat.completions.create(
        model = "gpt-4.1-mini",

        messages=formatted_messages,
        temperature=0.7,
        

    )

    return response.choices[0].message.content

async def stream_response(messages):

    formatted_messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT

        }
    ]

    for msg in messages:
        formatted_messages.append({
            "role":msg.role,
            "conetent":msg.content
        })

    stream = await client.chat.completions.create(
        model= "gpt-4.1-mini",
        messages=formatted_messages,
        stream = True
    )

    async for chunk in stream:

        content = chunk.choices[0].delta.content

        if content:
            yield content