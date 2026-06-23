from langchain_core.prompts import PromptTemplate

booking_extraction_prompt = PromptTemplate(
    input_variables=["question"],
    template=(
        "Extract booking details from the user's request.\n\n"
        "Question:\n{question}\n\n"
        "Return JSON only. Use null for any missing fields.\n"
        '{{\n'
        '  "pickup_location": null,\n'
        '  "destination": null,\n'
        '  "travel_date": null,\n'
        '  "vehicle_type": null\n'
        '}}'
    ),
)