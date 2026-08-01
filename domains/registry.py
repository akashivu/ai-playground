from domains.elixway.config import ENABLED_INTENTS as ELIXWAY_INTENTS
from domains.elixway.system_prompt import SYSTEM_PROMPT as ELIXWAY_PROMPT
from domains.elixway.knowledge.config import COLLECTION_NAME as ELIXWAY_COLLECTION
from domains.elixway.policy import ELIXWAY_POLICY

DOMAINS: dict[str, dict] = {
    "elixway": {
        "enabled_intents": ELIXWAY_INTENTS,
        "system_prompt": ELIXWAY_PROMPT,
        "collection_name": ELIXWAY_COLLECTION,
        "policy": ELIXWAY_POLICY,
    },
}