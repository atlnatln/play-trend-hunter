"""
Trend detection engine — multiple algorithms.
Compares current snapshot against historical data and calculates a surge score.
Designed for daily single-run execution (local PC, not always-on).
"""
import json

import config


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


def parse_historical_ranks(rows: list[dict]) -> dict[str, list[int]]:
    """Build app_id -> list of all historical rank positions."""
    result = {}
    for r in rows:
        app_id = r["app_id"]
        result.setdefault(app_id, []).append(r["rank_position"])
    return result


def parse_recent_worst_rank(rows: list[dict], max_snapshots: int = 3) -> dict[str, int]:
    """
    For each app, find the WORST (highest number) rank within the most
    recent N snapshots. This captures near-term momentum without
    accumulating stale data from a full 7-day window.
    """
    times = sorted({r["snapshot_at"] for r in rows}, reverse=True)
    recent_times = set(times[:max_snapshots])

    result = {}
    for r in rows:
        if r["snapshot_at"] not in recent_times:
            continue
        app_id = r["app_id"]
        rank = r["rank_position"]
        result[app_id] = max(result.get(app_id, rank), rank)
    return result


def parse_weighted_average_rank(rows: list[dict], max_snapshots: int = 3) -> dict[str, float]:
    """
    Weighted Moving Average of ranks over the last N snapshots.
    More recent snapshots get higher weight.
    Weights: [3, 2, 1] for last 3 days.
    """
    times = sorted({r["snapshot_at"] for r in rows}, reverse=True)
    recent_times = times[:max_snapshots]

    # Group ranks by snapshot_at (most recent first)
    ranks_by_time = {}
    for r in rows:
        if r["snapshot_at"] not in recent_times:
            continue
        app_id = r["app_id"]
        ranks_by_time.setdefault(app_id, {})[r["snapshot_at"]] = r["rank_position"]

    result = {}
    weights = list(range(len(recent_times), 0, -1))  # [3, 2, 1] for 3 snapshots
    for app_id, time_map in ranks_by_time.items():
        total = 0.0
        weight_sum = 0
        for i, t in enumerate(recent_times):
            if t in time_map:
                w = weights[i]
                total += time_map[t] * w
                weight_sum += w
        if weight_sum > 0:
            result[app_id] = total / weight_sum
    return result


def parse_slope(rows: list[dict], max_snapshots: int = 4) -> dict[str, tuple[float, float]]:
    """
    Linear regression slope and R-squared over the last N snapshots.
    Returns (slope, r2) where:
      - slope: negative = climbing up, positive = dropping down
      - r2: fit quality 0-1 (1 = perfect straight-line trend)
    Uses ordinary least squares: y = mx + b
    """
    times = sorted({r["snapshot_at"] for r in rows}, reverse=True)
    recent_times = times[:max_snapshots][::-1]  # oldest first for x=0,1,2...

    # Group ranks by snapshot_at
    ranks_by_time = {}
    for r in rows:
        if r["snapshot_at"] not in recent_times:
            continue
        app_id = r["app_id"]
        ranks_by_time.setdefault(app_id, {})[r["snapshot_at"]] = r["rank_position"]

    result = {}
    for app_id, time_map in ranks_by_time.items():
        x_vals = []
        y_vals = []
        for i, t in enumerate(recent_times):
            if t in time_map:
                x_vals.append(i)
                y_vals.append(time_map[t])

        n = len(x_vals)
        if n < 3:
            continue

        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(x * x for x in x_vals)
        sum_y2 = sum(y * y for y in y_vals)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            continue

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - slope * sum_x) / n

        ss_res = sum((y - (slope * x + b)) ** 2 for x, y in zip(x_vals, y_vals))
        ss_tot = sum((y - sum_y / n) ** 2 for y in y_vals)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0

        result[app_id] = (slope, r2)

    return result


def _compute_ratings_score(prev, curr):
    if prev and curr["ratings"] and prev["ratings"]:
        ratings_delta = curr["ratings"] - prev["ratings"]
        signals = {}
        if ratings_delta > 0:
            signals = {
                "previous": prev["ratings"],
                "current": curr["ratings"],
                "delta": ratings_delta,
            }
        return min(ratings_delta / 100, 50), signals
    return 0, {}


def _compute_score_score(prev, curr):
    if prev and curr["score"] and prev["score"]:
        score_delta = curr["score"] - prev["score"]
        signals = {}
        if score_delta > 0:
            signals = {
                "previous": prev["score"],
                "current": curr["score"],
                "delta": round(score_delta, 3),
            }
        return max(0, score_delta * 20), signals
    return 0, {}


def _build_alert(app_id, curr, collection, category, surge_score, signals):
    return {
        "app_id": app_id,
        "title": curr["title"],
        "collection": collection,
        "category": category,
        "surge_score": round(surge_score, 2),
        "current_rank": curr["rank"],
        "signals": signals,
    }


def detect_surges_recent(
    current_rows: list[dict],
    previous_rows: list[dict],
    historical_rows: list[dict],
    collection: str,
    category: str,
) -> list[dict]:
    """
    ALGO: recent-delta (3-day window)
    Core signal: last 3 days' worst rank -> current.
    Clean, low-noise, misses apps that spiked earlier and went flat.
    """
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    historical_ranks = parse_historical_ranks(historical_rows)
    recent_worst = parse_recent_worst_rank(historical_rows, max_snapshots=3)
    alerts = []

    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)

        past_ranks = historical_ranks.get(app_id, [])

        # Volatility filter: skip apps that bounce up/down constantly
        if len(past_ranks) >= 3:
            mean_rank = sum(past_ranks) / len(past_ranks)
            variance = sum((r - mean_rank) ** 2 for r in past_ranks) / len(past_ranks)
            std_dev = variance ** 0.5
            if std_dev > 35:
                continue  # Too volatile, skip

        if not past_ranks:
            signals["newcomer"] = {
                "current_rank": curr["rank"],
                "note": "Entered top list within tracked window",
            }
            rank_delta_score = max(0, 50 - curr["rank"])
            newcomer_bonus = 5
        else:
            newcomer_bonus = 0
            worst_rank = recent_worst.get(app_id, curr["rank"])
            recent_delta = worst_rank - curr["rank"]
            if recent_delta > 0:
                signals["rank_delta"] = {
                    "worst_rank": worst_rank,
                    "current_rank": curr["rank"],
                    "recent_delta": recent_delta,
                    "window_days": 3,
                }
            rank_delta_score = max(0, recent_delta)

        ratings_score, ratings_signals = _compute_ratings_score(prev, curr)
        if ratings_signals:
            signals["ratings_delta"] = ratings_signals

        score_score, score_signals = _compute_score_score(prev, curr)
        if score_signals:
            signals["score_delta"] = score_signals

        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus

        if surge_score >= config.SURGE_THRESHOLD:
            alerts.append(_build_alert(app_id, curr, collection, category, surge_score, signals))

    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts


def detect_surges_persistence(
    current_rows: list[dict],
    previous_rows: list[dict],
    historical_rows: list[dict],
    collection: str,
    category: str,
) -> list[dict]:
    """
    ALGO: persistence (recent-delta + cumulative bonus for top-ranked apps)

    Recent delta catches apps moving NOW.
    Persistence bonus catches apps that spiked earlier and are still
    holding a strong position (top 50). This brings back IQ Masters-style
    candidates without the full 7-day cumulative noise.
    """
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    historical_ranks = parse_historical_ranks(historical_rows)
    recent_worst = parse_recent_worst_rank(historical_rows, max_snapshots=3)
    alerts = []

    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)

        past_ranks = historical_ranks.get(app_id, [])
        if not past_ranks:
            signals["newcomer"] = {
                "current_rank": curr["rank"],
                "note": "Entered top list within tracked window",
            }
            rank_delta_score = max(0, 50 - curr["rank"])
            newcomer_bonus = 15
        else:
            newcomer_bonus = 0
            worst_rank = recent_worst.get(app_id, curr["rank"])
            recent_delta = worst_rank - curr["rank"]
            if recent_delta > 0:
                signals["rank_delta"] = {
                    "worst_rank": worst_rank,
                    "current_rank": curr["rank"],
                    "recent_delta": recent_delta,
                    "window_days": 3,
                }
            rank_delta_score = max(0, recent_delta)

            # --- Persistence bonus ---
            if curr["rank"] <= 50:
                historical_worst = max(past_ranks)
                cumulative_delta = historical_worst - curr["rank"]
                if cumulative_delta > recent_delta:
                    persistence_bonus = min(round(cumulative_delta * 0.3, 2), 30)
                    if persistence_bonus > 0:
                        signals["persistence"] = {
                            "historical_worst": historical_worst,
                            "cumulative_delta": cumulative_delta,
                            "persistence_bonus": persistence_bonus,
                            "reason": "Still top-50 after strong climb",
                        }
                    rank_delta_score += persistence_bonus

        ratings_score, ratings_signals = _compute_ratings_score(prev, curr)
        if ratings_signals:
            signals["ratings_delta"] = ratings_signals

        score_score, score_signals = _compute_score_score(prev, curr)
        if score_signals:
            signals["score_delta"] = score_signals

        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus

        if surge_score >= config.SURGE_THRESHOLD:
            alerts.append(_build_alert(app_id, curr, collection, category, surge_score, signals))

    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts


def detect_surges_wma(
    current_rows: list[dict],
    previous_rows: list[dict],
    historical_rows: list[dict],
    collection: str,
    category: str,
) -> list[dict]:
    """
    ALGO: weighted-moving-average (3-day WMA vs current)

    Weights recent days more heavily. An app that was #100, #80, #60
    over the last 3 days has WMA ~73. If today it's #40, delta = 33.
    Smoother than raw worst-rank delta, less sensitive to single-day spikes.
    """
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    historical_ranks = parse_historical_ranks(historical_rows)
    wma_ranks = parse_weighted_average_rank(historical_rows, max_snapshots=3)
    alerts = []

    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)

        past_ranks = historical_ranks.get(app_id, [])
        if not past_ranks:
            signals["newcomer"] = {
                "current_rank": curr["rank"],
                "note": "Entered top list within tracked window",
            }
            rank_delta_score = max(0, 50 - curr["rank"])
            newcomer_bonus = 15
        else:
            newcomer_bonus = 0
            wma_rank = wma_ranks.get(app_id, float(curr["rank"]))
            wma_delta = round(wma_rank - curr["rank"], 2)
            if wma_delta > 0:
                signals["rank_delta"] = {
                    "wma_rank": round(wma_rank, 1),
                    "current_rank": curr["rank"],
                    "wma_delta": wma_delta,
                    "window_days": 3,
                }
            rank_delta_score = max(0, wma_delta)

        ratings_score, ratings_signals = _compute_ratings_score(prev, curr)
        if ratings_signals:
            signals["ratings_delta"] = ratings_signals

        score_score, score_signals = _compute_score_score(prev, curr)
        if score_signals:
            signals["score_delta"] = score_signals

        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus

        if surge_score >= config.SURGE_THRESHOLD:
            alerts.append(_build_alert(app_id, curr, collection, category, surge_score, signals))

    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts


def detect_surges_slope(
    current_rows: list[dict],
    previous_rows: list[dict],
    historical_rows: list[dict],
    collection: str,
    category: str,
) -> list[dict]:
    """
    ALGO: linear-regression slope (4-day trend)

    Fits a line to the last 4 snapshots' ranks.
    Negative slope = consistent upward climb.
    Score = -slope * 3 (scale factor tuned so ~10 ranks/day = threshold 30).

    Only accepts apps with R² >= 0.5 (decent straight-line fit) so that
    random daily wiggles don't trigger false alerts.

    Catches steady climbers that other algorithms might miss because
    no single day had a huge jump.
    """
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    historical_ranks = parse_historical_ranks(historical_rows)
    slopes = parse_slope(historical_rows, max_snapshots=4)
    alerts = []

    SLOPE_SCALE = 3.0
    MIN_R2 = 0.5

    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)

        past_ranks = historical_ranks.get(app_id, [])
        if not past_ranks:
            signals["newcomer"] = {
                "current_rank": curr["rank"],
                "note": "Entered top list within tracked window",
            }
            rank_delta_score = max(0, 50 - curr["rank"])
            newcomer_bonus = 15
        else:
            newcomer_bonus = 0
            slope_info = slopes.get(app_id)
            if slope_info is None:
                rank_delta_score = 0
            else:
                slope, r2 = slope_info
                if r2 < MIN_R2:
                    rank_delta_score = 0
                else:
                    trend_score = max(0, -slope * SLOPE_SCALE)
                    if trend_score > 0:
                        signals["rank_delta"] = {
                            "slope_per_day": round(slope, 2),
                            "r_squared": round(r2, 3),
                            "current_rank": curr["rank"],
                            "trend_score": round(trend_score, 2),
                            "window_days": 4,
                        }
                    rank_delta_score = trend_score

        ratings_score, ratings_signals = _compute_ratings_score(prev, curr)
        if ratings_signals:
            signals["ratings_delta"] = ratings_signals

        score_score, score_signals = _compute_score_score(prev, curr)
        if score_signals:
            signals["score_delta"] = score_signals

        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus

        if surge_score >= config.SURGE_THRESHOLD:
            alerts.append(_build_alert(app_id, curr, collection, category, surge_score, signals))

    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts
