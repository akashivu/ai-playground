from dataclasses import dataclass


@dataclass(frozen=True)
class DomainPolicy:
    domain_name: str
    allowed_topics: list[str]
    restricted_capabilities: list[str]
    refusal_message: str