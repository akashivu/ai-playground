from langchain_components.knowledge.vehicle_store import VEHICLES, MAX_CAPACITY


def recommend_vehicles(passengers: int) -> list[dict]:
    """Returns all vehicles that can accommodate the given passenger count."""
    return [v for v in VEHICLES if v["capacity"] >= passengers]


def format_recommendations(vehicles: list[dict]) -> str:
    """Formats vehicle recommendations into a readable response."""
    if not vehicles:
        return (
            f"We currently don't have a vehicle for your group size. "
            f"Our largest vehicle accommodates {MAX_CAPACITY} passengers. "
            "Please contact AdiyogiCabz for custom arrangements."
        )

    lines = ["Here are the recommended vehicles for your trip:\n"]
    for v in vehicles:
        lines.append(f"• {v['name']} — up to {v['capacity']} passengers")
        lines.append(f"  {v['description']}")

    lines.append("\nWould you like to proceed with a booking?")
    return "\n".join(lines)