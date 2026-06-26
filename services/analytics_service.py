import sqlite3
from utils.logger import logger


class AnalyticsService:
    """Provides usage and cost analytics from SQLite logs."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self.db_path = db_path

    def total_requests(self) -> int:
        """Returns total number of requests logged."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM usage_logs").fetchone()[0]

    def total_sessions(self) -> int:
        """Returns total number of unique sessions."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT COUNT(DISTINCT session_id) FROM usage_logs"
            ).fetchone()[0]

    def average_latency(self) -> float:
        """Returns average response latency in seconds."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT AVG(latency) FROM usage_logs").fetchone()[0]
        return round(result or 0.0, 4)

    def top_intents(self, limit: int = 10) -> list[dict]:
        """Returns top intents by request count."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT intent, COUNT(*) as count
                FROM usage_logs
                GROUP BY intent
                ORDER BY count DESC
                LIMIT ?
            """, (limit,)).fetchall()
        return [{"intent": r[0], "count": r[1]} for r in rows]

    def daily_requests(self, days: int = 7) -> list[dict]:
        """Returns daily request counts for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM usage_logs
                WHERE created_at >= DATE('now', ?)
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (f"-{days} days",)).fetchall()
        return [{"date": r[0], "count": r[1]} for r in rows]

    def slowest_intents(self, limit: int = 5) -> list[dict]:
        """Returns intents with highest average latency."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT intent, ROUND(AVG(latency), 4) as avg_latency
                FROM usage_logs
                GROUP BY intent
                ORDER BY avg_latency DESC
                LIMIT ?
            """, (limit,)).fetchall()
        return [{"intent": r[0], "avg_latency": r[1]} for r in rows]

    def total_tokens(self) -> int:
        """Returns total tokens consumed across all requests."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT SUM(total_tokens) FROM token_usage_logs"
            ).fetchone()[0]
        return result or 0

    def total_cost(self) -> float:
        """Returns total estimated cost in USD."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT SUM(estimated_cost) FROM token_usage_logs"
            ).fetchone()[0]
        return round(result or 0.0, 6)

    def cost_by_intent(self) -> list[dict]:
        """Returns estimated cost grouped by intent, highest first."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT intent, ROUND(SUM(estimated_cost), 6) as total_cost
                FROM token_usage_logs
                GROUP BY intent
                ORDER BY total_cost DESC
            """).fetchall()
        return [{"intent": r[0], "total_cost": r[1]} for r in rows]

    def daily_cost(self, days: int = 7) -> list[dict]:
        """Returns daily cost for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT DATE(created_at) as date,
                       ROUND(SUM(estimated_cost), 6) as cost
                FROM token_usage_logs
                WHERE created_at >= DATE('now', ?)
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (f"-{days} days",)).fetchall()
        return [{"date": r[0], "cost": r[1]} for r in rows]


analytics_service = AnalyticsService()