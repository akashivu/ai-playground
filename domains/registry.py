from domains.adiyogicabz.config import ENABLED_INTENTS as ADIYOGICABZ_INTENTS
from domains.adiyogicabz.system_prompt import SYSTEM_PROMPT as ADIYOGICABZ_PROMPT
from domains.adiyogicabz.knowledge.config import COLLECTION_NAME as ADIYOGICABZ_COLLECTION

DOMAINS: dict[str, dict] = {
    "adiyogicabz": {
        "enabled_intents": ADIYOGICABZ_INTENTS,
        "system_prompt": ADIYOGICABZ_PROMPT,
        "collection_name": ADIYOGICABZ_COLLECTION,
    },
}