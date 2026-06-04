from langchain_core.prompts import (PromptTemplate,)

evaluation_prompt = PromptTemplate(
    input_variables=[
        "question",
        "context",
        "answer",
    ],

    template="""
Question:
{question}

Context:
{context}

Answer:
{answer}

Evaluate whether the answer
is grounded in the provided context.

Return JSON only using
this exact schema:

{{
    "score": 0-10,
    "grounded": true,
    "reason": "short explanation"
}}
""",
)