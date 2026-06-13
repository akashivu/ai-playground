from langchain_components.routing.intent_types import IntentType

WORKFLOWS: dict[IntentType, callable] = {}


def register_workflow(intent: IntentType):
    """Decorator that registers a workflow function for a given intent."""
    def decorator(workflow: callable) -> callable:
        WORKFLOWS[intent] = workflow
        return workflow
    return decorator