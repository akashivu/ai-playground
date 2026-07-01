from langchain_core.prompts import PromptTemplate

recommendation_extraction_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You extract vehicle recommendation information.

Return ONLY valid JSON.

If a value is missing, return null.

{
  "passengers": null,
  "trip_type": null,
  "needs_luggage": null
}

User message:

{question}
"""
)
