from typing import TypedDict

class ConversationState(TypedDict,total=False,):
    question: str
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
    retry_count: int
    max_retries: int
    collection: str
    session_id: str
    history: list