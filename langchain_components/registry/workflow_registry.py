from typing import Callable
from langchain_components.routing.intent_types import (IntentType,)

WORKFLOWS: dict[
    IntentType,
    Callable,
] = {}