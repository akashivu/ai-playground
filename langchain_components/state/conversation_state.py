from typing import TypedDict


class ConversationState(TypedDict,total=False,):
    question: str
    rewritten_query: str
    context: str
    answer: str
    evaluation: dict