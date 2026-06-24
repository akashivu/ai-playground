from langchain_core.prompts import PromptTemplate

booking_status_prompt = PromptTemplate(
    input_variables=["question"],
    template=(
        "Extract the booking ID from the user's request.\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only. Use null if no booking ID is found.\n"
        '{{"booking_id": null}}'
    ),
)