import os
from domains.registry import DOMAINS
from langchain_components.guardrails.domain_policy import DomainPolicy


ACTIVE_DOMAIN = os.getenv("ACTIVE_DOMAIN", "adiyogicabz")


def get_active_domain() -> dict:
    """Returns the active domain configuration."""
    domain = DOMAINS.get(ACTIVE_DOMAIN)
    if domain is None:
        raise ValueError(f"Domain '{ACTIVE_DOMAIN}' is not registered in DOMAINS.")
    return domain


def get_system_prompt() -> str:
    """Returns the system prompt for the active domain."""
    return get_active_domain()["system_prompt"]


def get_collection_name() -> str:
    """Returns the knowledge base collection name for the active domain."""
    return get_active_domain()["collection_name"]

def get_policy() -> DomainPolicy:
    """Returns the active domain's policy configuration."""
    return get_active_domain()["policy"]
