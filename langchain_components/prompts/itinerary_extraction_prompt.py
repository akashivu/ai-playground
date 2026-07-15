from langchain_core.prompts import PromptTemplate


itinerary_extraction_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are an itinerary information extractor.

Extract ONLY the information explicitly mentioned.

Return JSON only.

{
  "destination": null,
  "days": null,
  "budget": null,
  "travelers": null,
  "interests": null
}

Question:

{question}
""",
)