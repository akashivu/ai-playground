from langchain_core.prompts import (PromptTemplate,)

query_rewrite_prompt = PromptTemplate(
    input_variables=[
        "history",
        "question",
    ],

    template="""
Conversation:

{history}

Question:

{question}

Rewrite the latest user question
into a standalone search query.

Return only the rewritten query.
""",
)