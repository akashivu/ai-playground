from typing import TypedDict


class ConversationState(TypedDict, total=False):
    session_id: str
    user_id: str
    email: str | None
    role: str

    question: str
    history: list

    booking_details: dict
    recommendation_details: dict
    itinerary_details: dict

    messages: list
    rewritten_query: str
    context: str
    answer: str
    evaluation: dict
    tool_calls: list
    tool_result: str
    iterations: int
    max_iterations: int
    retrieval_successful: bool
    retrieval_relevant: bool
    retrieval_failure_reason: str | None
    retry_count: int
    max_retries: int
    collection: str
    results: list