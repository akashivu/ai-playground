import sqlite3
from datetime import datetime
from utils.logger import logger


class TokenTrackingService:
    """Logs LLM token usage and estimated cost to SQLite."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self.db_path = db_path

    def log_usage(
        self,
        session_id: str,
        intent: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        estimated_cost: float,
    ) -> None:
        """Persists token usage for a single LLM call."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO token_usage_logs (
                        session_id, intent, model,
                        prompt_tokens, completion_tokens, total_tokens,
                        estimated_cost, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, intent, model,
                    prompt_tokens, completion_tokens, total_tokens,
                    estimated_cost, datetime.now().isoformat(),
                ))
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")


token_tracking_service = TokenTrackingService()