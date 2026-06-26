from fastapi import APIRouter
from services.analytics_service import analytics_service

router = APIRouter()


@router.get("/analytics")
def get_analytics() -> dict:
    """Returns platform usage analytics."""
    return {
        "total_requests": analytics_service.total_requests(),
        "total_sessions": analytics_service.total_sessions(),
        "average_latency": analytics_service.average_latency(),
        "top_intents": analytics_service.top_intents(),
        "daily_requests": analytics_service.daily_requests(days=7),
        "slowest_intents": analytics_service.slowest_intents(),
    }


@router.get("/analytics/cost")
def get_cost_analytics() -> dict:
    """Returns token usage and cost analytics."""
    return {
        "total_tokens": analytics_service.total_tokens(),
        "total_cost_usd": analytics_service.total_cost(),
        "cost_by_intent": analytics_service.cost_by_intent(),
        "daily_cost": analytics_service.daily_cost(days=7),
    }