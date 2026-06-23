from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.chains.recommendation_extraction_chain import recommendation_extraction_chain
from services.vehicle_recommendation_service import recommend_vehicles, format_recommendations


@register_workflow(IntentType.RECOMMENDATION)
def recommendation_workflow(state: dict) -> dict:
    """Recommends vehicles based on passenger count and trip requirements."""
    details = recommendation_extraction_chain.invoke({"question": state["question"]})

    raw_passengers = details.get("passengers")

    if raw_passengers is None:
        return {"answer": "How many passengers will be travelling?"}

    try:
        passengers = int(raw_passengers)
    except (ValueError, TypeError):
        return {"answer": "Could you tell me the number of passengers as a number? For example: 4, 7, 12."}

    if passengers <= 0:
        return {"answer": "Please provide a valid number of passengers."}

    vehicles = recommend_vehicles(passengers)
    answer = format_recommendations(vehicles)

    return {
        "answer": answer,
        "recommendation_details": {
            "passengers": passengers,
            "trip_type": details.get("trip_type"),
            "needs_luggage": details.get("needs_luggage"),
            "recommended_vehicles": [v["name"] for v in vehicles],
        },
    }