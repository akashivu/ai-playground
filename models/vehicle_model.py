from dataclasses import dataclass


@dataclass
class Vehicle:
    name: str
    capacity: int
    description: str
    best_for: list[str]