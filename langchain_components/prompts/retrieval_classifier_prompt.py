from langchain_core.prompts import PromptTemplate

retrieval_classifier_prompt = PromptTemplate(
    input_variables=["question"],
    template=(
        "Determine whether the question requires knowledge-base retrieval.\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only:\n"
        '{{"requires_retrieval": true}}\n'
        "or\n"
        '{{"requires_retrieval": false}}'
    ),
)