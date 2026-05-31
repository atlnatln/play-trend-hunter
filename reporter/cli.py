"""
CLI reporter for surge alerts.
"""


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
                print(f"     → Rank: #{sig_data['previous']} → #{sig_data['current']} (Δ {sig_data['delta']:+d})")
            elif sig_name == "ratings_delta":
                print(f"     → Ratings: +{sig_data['delta']:,}")
            elif sig_name == "score_delta":
                print(f"     → Score: {sig_data['previous']:.2f} → {sig_data['current']:.2f} (Δ {sig_data['delta']:+.3f})")
        print()
