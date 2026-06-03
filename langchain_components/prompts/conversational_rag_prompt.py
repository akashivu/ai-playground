from langchain_core.prompts import (ChatPromptTemplate,  MessagesPlaceholder,)

conversational_rag_prompt = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful AI assistant.

Use only the provided context.
""",
            ),

            MessagesPlaceholder(
                variable_name="history",
            ),

            (
                "human",
                """
Context:

{context}

Question:

{question}
""",
            ),
        ]
    )
)