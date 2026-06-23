from langchain_components.routing.intent_types import IntentType


def test_intent_enum_values():
    values = [item.value for item in IntentType]
    assert "GENERAL" in values
    assert "KNOWLEDGE_SEARCH" in values
    assert "FAQ" in values
    assert "BOOKING" in values
    assert "RECOMMENDATION" in values
    assert "PRICING" in values
    assert "OUT_OF_DOMAIN" in values


def test_intent_enum_from_string():
    intent = IntentType("PRICING")
    assert intent == IntentType.PRICING


def test_intent_enum_invalid_raises():
    try:
        IntentType("INVALID")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_intent_values_method():
    values = IntentType.values()
    assert isinstance(values, list)
    assert len(values) == 7