from langchain_components.registry.workflow_registry import WORKFLOWS
from langchain_components.routing.intent_types import IntentType


class WorkflowExecutor:
    """Executes workflows based on classified intents."""

    def execute(self, intent: IntentType, state: dict) -> dict:
        """Looks up and executes the workflow registered for the given intent."""
        workflow = WORKFLOWS.get(intent)
        if workflow is None:
            raise ValueError(f"No workflow registered for intent: '{intent}'.")
        return workflow(state)