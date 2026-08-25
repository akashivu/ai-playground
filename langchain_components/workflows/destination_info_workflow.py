from __future__ import annotations

from langchain_core.prompts import PromptTemplate

from config.llm_config import get_llm

from langchain_components.registry.workflow_decorator import (
    register_workflow,
)

from langchain_components.routing.intent_types import IntentType


destination_info_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are Elixway's destination information assistant.

The user is asking about a specific travel destination.

Rules:

1. This temporary destination feature supports Indian destinations only.
2. Give useful, concise, general destination information.
3. You may cover:
   - overview
   - why visit
   - attractions
   - things to do
   - food
   - travel tips
   - ideal trip duration
4. Do not invent exact prices, live availability, opening hours,
   current weather, or other time-sensitive information.
5. Do not claim live or real-time information.
6. Do not create a day-by-day itinerary unless the user explicitly
   asks for one. The itinerary workflow handles that.
7. If the requested destination is outside India, explain that this
   temporary destination feature supports India only and suggest
   that the user choose an Indian destination.
8. Keep the answer natural and useful.
9. Return plain text only.

User request:
{question}
""",
)


destination_info_chain = (
    destination_info_prompt
    | get_llm(temperature=0)
)


@register_workflow(IntentType.DESTINATION_INFO)
def destination_info_workflow(state: dict) -> dict:
    question = str(
        state.get("question") or ""
    ).strip()

    if not question:
        return {
            "answer": "Which destination would you like to know about?",
            "completed": False,
        }

    answer = destination_info_chain.invoke(
        {
            "question": question,
        }
    )

    return {
        "answer": str(answer),
        "completed": True,
    }