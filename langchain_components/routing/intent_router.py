from langchain_components.routing.intent_classifier_chain import intent_classifier_chain
from langchain_components.routing.intent_types import IntentType
from langchain_components.routing.intent_validator import validate_intent
from langchain_components.workflows.workflow_executor import WorkflowExecutor


workflow_executor = WorkflowExecutor()


def route_question(state: dict) -> dict:
    """Classifies, validates, and routes the question to the correct workflow."""
    question = state.get("question", "")

    result = intent_classifier_chain.invoke({"question": question})

    try:
        intent = IntentType(result.get("intent", "GENERAL"))
    except ValueError:
        intent = IntentType.GENERAL

    try:
        validate_intent(intent)
    except ValueError:
        intent = IntentType.GENERAL

    return workflow_executor.execute(intent=intent, state=state)