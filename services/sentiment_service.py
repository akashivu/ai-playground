from openai import OpenAI
from dotenv import load_dotenv
from prompts.sentiment_prompt import SENTIMENT_PROMPT

import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_sentiment(messages: str):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SENTIMENT_PROMPT},
            {"role": "user", "content": messages},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
