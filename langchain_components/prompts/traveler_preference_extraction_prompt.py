from langchain_core.prompts import PromptTemplate


traveler_preference_extraction_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You extract explicit travel preferences from a user's message.

Return ONLY valid JSON.

Rules:

1. Extract only preferences explicitly stated by the user.
2. Do not infer permanent preferences from a single destination choice.
3. Do not infer preferences from unsupported assumptions.
4. If a field is not explicitly stated, return null or [] as appropriate.
5. Do not extract destination, dates, or trip duration unless they are
   clearly stated as a preference.
6. Normalize preference values to simple lowercase phrases.

Return exactly:

{
  "interests": [],
  "travel_styles": [],
  "preferred_pace": null,
  "traveling_with": [],
  "budget_level": null,
  "favorite_destinations": [],
  "avoided_preferences": []
}

User message:
{question}
""",
)