from typing import List, Dict, Any


class ReportService:
    """Formats comparison tables and metrics rankings for logging and UI dashboards."""

    def format_rankings(self, comparison_table: List[Dict[str, Any]]) -> str:
        lines = []
        lines.append("Algorithm Comparison Rankings:")
        lines.append(f"{'Rank':<5} | {'Algorithm':<25} | {'Val Score':<10} | {'CV Score':<10} | {'Winner':<6}")
        lines.append("-" * 70)
        for item in comparison_table:
            winner_str = "YES" if item["winner_flag"] else "NO"
            lines.append(
                f"{item['ranking']:<5} | {item['algorithm']:<25} | "
                f"{item['validation_score']:<10.4f} | {item['cross_validation_score']:<10.4f} | {winner_str:<6}"
            )
        return "\n".join(lines)
