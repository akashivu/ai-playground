from langchain_core.prompts import ChatPromptTemplate

hallucination_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You detect hallucinations.

Determine whether the answer contains information that is NOT present in the context.

Return ONLY valid JSON.

{
    "hallucination": true,
    "reason": "..."
}
"""
    ),
    (
        "human",
        """
Context:

{context}

Answer:

{answer}
"""
    ),
])