"""
Trend detection engine.
Compares two snapshots and calculates a surge score.
"""
import json
from datetime import datetime


def parse_snapshot(rows: list[dict]) -> dict[str, dict]:
    """Convert snapshot rows to app_id -> data map."""
    result = {}
    for r in rows:
        result[r["app_id"]] = {
            "title": r["title"],
            "rank": r["rank_position"],
            "score": r["score"],
            "ratings": r["ratings"] or 0,
            "developer": r["developer"],
            "genre": r["genre"],
            "snapshot_at": r["snapshot_at"],
        }
    return result


def detect_surges(
    current_rows: list[dict],
    previous_rows: list[dict],
    collection: str,
    category: str,
) -> list[dict]:
    """
    Compare two snapshots and return apps with significant positive momentum.
    """
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    alerts = []

    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)
        if not prev:
            # Newcomer to the list — strong signal
            signals["newcomer"] = {
                "current_rank": curr["rank"],
                "note": "Entered top list since last snapshot",
            }
            rank_delta_score = max(0, 50 - curr["rank"])  # Higher rank = more points
        else:
            rank_delta = prev["rank"] - curr["rank"]  # Positive = moved up
            signals["rank_delta"] = {
                "previous": prev["rank"],
                "current": curr["rank"],
                "delta": rank_delta,
            }
            rank_delta_score = max(0, rank_delta)

        # Review/ratings growth (if available)
        if prev and curr["ratings"] and prev["ratings"]:
            ratings_delta = curr["ratings"] - prev["ratings"]
            if ratings_delta > 0:
                signals["ratings_delta"] = {
                    "previous": prev["ratings"],
                    "current": curr["ratings"],
                    "delta": ratings_delta,
                }
            ratings_score = min(ratings_delta / 100, 50)  # Cap at 50
        else:
            ratings_score = 0

        # Score improvement
        if prev and curr["score"] and prev["score"]:
            score_delta = curr["score"] - prev["score"]
            if score_delta > 0:
                signals["score_delta"] = {
                    "previous": prev["score"],
                    "current": curr["score"],
                    "delta": round(score_delta, 3),
                }
            score_score = max(0, score_delta * 20)
        else:
            score_score = 0

        # Newcomer bonus
        newcomer_bonus = 15 if "newcomer" in signals else 0

        # Calculate surge score
        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus

        if surge_score > 5:  # Threshold
            alerts.append(
                {
                    "app_id": app_id,
                    "title": curr["title"],
                    "collection": collection,
                    "category": category,
                    "surge_score": round(surge_score, 2),
                    "current_rank": curr["rank"],
                    "signals": signals,
                }
            )

    # Sort by surge score descending
    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts

