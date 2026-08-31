from services.destination_resolver import get_destination_resolver


def test_resolve_exact_name() -> None:
    resolver = get_destination_resolver()
    result = resolver.resolve("Coorg")
    assert result.destination is not None
    assert result.destination.id == "coorg"
    assert result.confidence == 1.0


def test_resolve_case_insensitive() -> None:
    resolver = get_destination_resolver()
    result = resolver.resolve("COORG")
    assert result.destination is not None
    assert result.destination.id == "coorg"


def test_resolve_name_with_state() -> None:
    resolver = get_destination_resolver()
    result = resolver.resolve("Coorg, Karnataka")
    assert result.destination is not None
    assert result.destination.id == "coorg"


def test_unknown_destination() -> None:
    resolver = get_destination_resolver()
    result = resolver.resolve("Rishikesh")
    assert result.destination is None
    assert result.confidence == 0.0