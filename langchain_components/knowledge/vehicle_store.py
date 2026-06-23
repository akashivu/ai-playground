VEHICLES = [
    {
        "name": "Sedan",
        "capacity": 4,
        "description": "Suitable for small families and business travel.",
        "best_for": ["business", "airport", "short trips"],
    },
    {
        "name": "Toyota Innova",
        "capacity": 7,
        "description": "Comfortable for families and airport transfers.",
        "best_for": ["family", "airport", "outstation"],
    },
    {
        "name": "Tempo Traveller",
        "capacity": 12,
        "description": "Ideal for group travel and long-distance trips.",
        "best_for": ["group", "outstation", "pilgrimage"],
    },
    {
        "name": "Force Urbania",
        "capacity": 17,
        "description": "Premium vehicle for larger groups.",
        "best_for": ["large group", "corporate", "events"],
    },
]

MAX_CAPACITY = max(v["capacity"] for v in VEHICLES)