#!/usr/bin/env python3
"""
Play Trend Hunter — Main entry point.

Usage:
    python run.py scan              # Fetch latest snapshots for all tracked categories
    python run.py detect            # Compare latest two snapshots and detect surges
    python run.py full              # scan + detect
    python run.py detail <appId>    # Fetch full app details and reviews
    python run.py alerts            # Show recent alerts (chronological)
    python run.py top-alerts [N]    # Show top N alerts by score (default 10)
    python run.py auto-detail [N]   # Auto-fetch details for top N alerts (default 5)
    python run.py report            # Summary report of all snapshots and alerts
"""
import sys
from datetime import datetime, timezone

from database.models import init_db, save_snapshot, get_snapshots, save_app_detail, save_reviews, save_alert, get_recent_alerts, get_top_alerts, get_alert_count_by_category, get_snapshot_dates
from scraper.play_store import safe_fetch_list, fetch_app_detail, fetch_reviews, CacheGuard
from detector.surge import detect_surges
from reporter.cli import print_report, print_top_alerts
import config


def cmd_scan():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting scan for {len(config.TRACKED_CATEGORIES)} categories...")
    cache = CacheGuard(ttl_hours=config.CACHE_TTL_HOURS)
    snapshot_at = datetime.now(timezone.utc).isoformat()
    total = 0
    for collection in config.TRACKED_COLLECTIONS:
        for category in config.TRACKED_CATEGORIES:
            try:
                cached = cache.get("list", collection, category, config.FETCH_NUM)
                if cached:
                    print(f"  [CACHE] {collection}/{category} — using cached data")
                    apps = cached
                else:
                    print(f"  [FETCH] {collection}/{category} ...")
                    apps = safe_fetch_list(collection, category, config.FETCH_NUM, cache=cache)
                save_snapshot(apps, collection, category, snapshot_at)
                total += len(apps)
                print(f"  [OK] {collection}/{category}: {len(apps)} apps saved")
            except Exception as e:
                print(f"  [ERR] {collection}/{category}: {e}")
    print(f"[DONE] Scan complete. {total} total app positions saved.")


def cmd_detect():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Running surge detection...")
    all_alerts = []
    for collection in config.TRACKED_COLLECTIONS:
        for category in config.TRACKED_CATEGORIES:
            try:
                snaps = get_snapshots(collection, category, limit=2)
                if len(snaps) < 2:
                    continue
                # Partition by snapshot_at
                times = sorted(set(s["snapshot_at"] for s in snaps), reverse=True)
                if len(times) < 2:
                    continue
                current = [s for s in snaps if s["snapshot_at"] == times[0]]
                previous = [s for s in snaps if s["snapshot_at"] == times[1]]
                alerts = detect_surges(current, previous, collection, category)
                for a in alerts:
                    save_alert(a["app_id"], collection, category, a["surge_score"], a["signals"])
                all_alerts.extend(alerts)
            except Exception as e:
                print(f"  [ERR] {collection}/{category}: {e}")
    print_report(all_alerts)
    print(f"[DONE] {len(all_alerts)} alerts saved to database.")


def cmd_detail(app_id: str):
    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching details for {app_id}...")
    try:
        detail = fetch_app_detail(app_id)
        save_app_detail(detail)
        print(f"  Title: {detail.get('title')}")
        print(f"  Score: {detail.get('score')}")
        print(f"  Installs: {detail.get('installs')}")
        print(f"  Ratings: {detail.get('ratings')}")
        print(f"  Genre: {detail.get('genre')}")
        print(f"  Released: {detail.get('released')}")
        print(f"  Updated: {detail.get('updated')}")
        print(f"  Developer: {detail.get('developer')}")
        print(f"  IAP: {detail.get('offersIAP')}")
        print(f"  Ad Supported: {detail.get('adSupported')}")
    except Exception as e:
        print(f"  [ERR] detail fetch failed: {e}")
        return
    try:
        print(f"  Fetching recent reviews...")
        rev_data = fetch_reviews(app_id, num=50, sort="NEWEST")
        reviews = rev_data.get("data", [])
        save_reviews(app_id, reviews)
        print(f"  Saved {len(reviews)} reviews")
    except Exception as e:
        print(f"  [ERR] review fetch failed: {e}")


def cmd_alerts():
    alerts = get_recent_alerts(limit=50)
    print(f"\nRecent alerts ({len(alerts)}):\n")
    for a in alerts:
        sigs = a.get("signals", "{}")
        print(f"  [{a['detected_at']}] {a['app_id']} — score: {a['surge_score']} — {a['category']}")


def cmd_top_alerts(limit: int = 10):
    alerts = get_top_alerts(limit=limit)
    print_top_alerts(alerts, limit=limit)


def cmd_auto_detail(limit: int = 5):
    alerts = get_top_alerts(limit=limit)
    if not alerts:
        print("No alerts to fetch details for.")
        return
    print(f"Auto-fetching details for top {len(alerts)} alerts...\n")
    for a in alerts:
        cmd_detail(a["app_id"])
        print()


def cmd_report():
    print(f"\n{'=' * 70}")
    print(f" PLAY TREND HUNTER — REPORT")
    print(f"{'=' * 70}\n")
    dates = get_snapshot_dates()
    print(f"  Snapshots: {len(dates)}")
    if dates:
        print(f"  Latest:    {dates[0]}")
        print(f"  First:     {dates[-1]}\n")
    cats = get_alert_count_by_category()
    print(f"  Total alerts: {sum(c['cnt'] for c in cats)}")
    print(f"  Categories with alerts: {len(cats)}\n")
    print("  Top categories:")
    for c in cats[:10]:
        print(f"    {c['category']:<25}: {c['cnt']}")
    print()
    top = get_top_alerts(limit=5)
    if top:
        print("  Highest scoring alerts:")
        for a in top:
            title = a.get("title") or a["app_id"]
            print(f"    Score {a['surge_score']:>5} | {a['category']:<22} | {title}")
    print(f"\n{'=' * 70}\n")


def main():
    init_db()
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "scan":
        cmd_scan()
    elif cmd == "detect":
        cmd_detect()
    elif cmd == "full":
        cmd_scan()
        print()
        cmd_detect()
    elif cmd == "detail" and len(sys.argv) >= 3:
        cmd_detail(sys.argv[2])
    elif cmd == "alerts":
        cmd_alerts()
    elif cmd == "top-alerts":
        limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        cmd_top_alerts(limit=limit)
    elif cmd == "auto-detail":
        limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
        cmd_auto_detail(limit=limit)
    elif cmd == "report":
        cmd_report()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
