PRICING = {
    "gpt-4o-mini": {
        "input": 0.00000015,
        "output": 0.00000060,
    },
    "gpt-4o": {
        "input": 0.000005,
        "output": 0.000015,
    },
    "text-embedding-3-small": {
        "input": 0.00000002,
        "output": 0.0,
    },
}

DEFAULT_PRICING = {
    "input": 0.00000015,
    "output": 0.00000060,
}


class CostEstimationService:
    """Estimates LLM cost based on token usage and model pricing."""

    def estimate(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
    ) -> float:
        """Returns estimated cost in USD."""
        rates = PRICING.get(model, DEFAULT_PRICING)
        input_cost = prompt_tokens * rates["input"]
        output_cost = completion_tokens * rates["output"]
        return round(input_cost + output_cost, 8)


cost_estimation_service = CostEstimationService()