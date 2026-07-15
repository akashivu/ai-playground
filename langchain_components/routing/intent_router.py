from langchain_components.routing.intent_classifier_chain import intent_classifier_chain
from langchain_components.routing.intent_types import IntentType
from langchain_components.routing.intent_validator import validate_intent
from langchain_components.workflows.workflow_executor import WorkflowExecutor


workflow_executor = WorkflowExecutor()


def classify_intent(question: str) -> IntentType:
    """Classifies and validates the user's intent from a question string."""
    result = intent_classifier_chain.invoke({"question": question})

    print("=" * 60)
    print("QUESTION:", question)
    print("RAW LLM RESULT:", result)
    print("=" * 60)

    try:
        intent = IntentType(result.get("intent", "GENERAL"))
    except ValueError:
        intent = IntentType.GENERAL

    try:
         intent = validate_intent(intent)
         print("FINAL INTENT:", intent)
         return intent
    except ValueError:
        return IntentType.GENERAL


def execute_workflow(intent: IntentType, state: dict) -> dict:
    """Executes the registered workflow for the given intent and injects intent into result."""
    result = workflow_executor.execute(intent=intent, state=state)
    result["intent"] = intent.value
    return result


def route_question(state: dict) -> dict:
    """Backward-compatible wrapper: classifies intent then executes workflow."""
    intent = classify_intent(state["question"])
    return execute_workflow(intent=intent, state=state)
