"""
CLI reporter for surge alerts.
"""
import json


def print_top_alerts(alerts: list[dict], limit: int = 10):
    if not alerts:
        print("No surge alerts found.")
        return
    print(f"\n{'=' * 70}")
    print(f" TOP {min(limit, len(alerts))} SURGE ALERTS (by score)")
    print(f"{'=' * 70}\n")
    for i, a in enumerate(alerts[:limit], 1):
        title = a.get("title") or a["app_id"]
        rank = a.get("current_rank") or "?"
        print(f"  #{i} 🔥 {title} ({a['app_id']})")
        print(f"     Score: {a['surge_score']}  |  Rank: #{rank}  |  Cat: {a['category']}")
        sigs = json.loads(a["signals"]) if isinstance(a["signals"], str) else a["signals"]
        for sig_name, sig_data in sigs.items():
            if sig_name == "newcomer":
                print(f"     → Newcomer at rank #{sig_data['current_rank']}")
            elif sig_name == "rank_delta":
                prev = sig_data.get('previous') or sig_data.get('worst_rank')
                curr = sig_data.get('current') or sig_data.get('current_rank')
                delta = sig_data.get('delta') or sig_data.get('cumulative_delta') or sig_data.get('recent_delta')
                print(f"     → Rank: #{prev} → #{curr} (Δ {delta:+d})")
            elif sig_name == "ratings_delta":
                print(f"     → Ratings: +{sig_data['delta']:,}")
            elif sig_name == "score_delta":
                print(f"     → Score: {sig_data['previous']:.2f} → {sig_data['current']:.2f} (Δ {sig_data['delta']:+.3f})")
        print()


def print_report(alerts: list[dict]):
    if not alerts:
        print("No surge alerts detected.")
        return
    print(f"\n{'=' * 70}")
    print(f" SURGE ALERTS: {len(alerts)} apps detected")
    print(f"{'=' * 70}\n")
    for a in alerts:
        print(f"  🔥 {a['title']} ({a['app_id']})")
        print(f"     Score: {a['surge_score']}  |  Rank: #{a['current_rank']}  |  Cat: {a['category']}")
        for sig_name, sig_data in a["signals"].items():
            if sig_name == "newcomer":
                print(f"     → Newcomer at rank #{sig_data['current_rank']}")
            elif sig_name == "rank_delta":
                prev = sig_data.get('previous') or sig_data.get('worst_rank')
                curr = sig_data.get('current') or sig_data.get('current_rank')
                delta = sig_data.get('delta') or sig_data.get('cumulative_delta') or sig_data.get('recent_delta')
                print(f"     → Rank: #{prev} → #{curr} (Δ {delta:+d})")
            elif sig_name == "ratings_delta":
                print(f"     → Ratings: +{sig_data['delta']:,}")
            elif sig_name == "score_delta":
                print(f"     → Score: {sig_data['previous']:.2f} → {sig_data['current']:.2f} (Δ {sig_data['delta']:+.3f})")
        print()
