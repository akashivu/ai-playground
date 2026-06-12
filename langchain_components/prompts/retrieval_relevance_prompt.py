from langchain_core.prompts import PromptTemplate

retrieval_relevance_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template=(
        "Question:\n{question}\n\n"
        "Context:\n{context}\n\n"
        "Determine whether the context is relevant to the question.\n\n"
        "Return JSON only:\n"
        '{{"relevant": true}}\n'
        "or\n"
        '{{"relevant": false}}'
    ),
)