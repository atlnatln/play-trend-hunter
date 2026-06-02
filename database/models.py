"""
SQLite schema for Play Store trend tracking.
All timestamps are UTC.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent.parent / "data" / "play_trend.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_at TEXT NOT NULL,
        collection TEXT NOT NULL,
        category TEXT NOT NULL,
        app_id TEXT NOT NULL,
        title TEXT,
        developer TEXT,
        score REAL,
        ratings INTEGER,
        installs TEXT,
        genre TEXT,
        rank_position INTEGER NOT NULL,
        raw_json TEXT,
        UNIQUE(snapshot_at, collection, category, app_id)
    );

    CREATE INDEX IF NOT EXISTS idx_snap_app ON snapshots(app_id, snapshot_at);
    CREATE INDEX IF NOT EXISTS idx_snap_cat ON snapshots(collection, category, snapshot_at);

    CREATE TABLE IF NOT EXISTS app_details (
        app_id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        summary TEXT,
        installs TEXT,
        score REAL,
        ratings INTEGER,
        reviews INTEGER,
        price REAL,
        free INTEGER,
        genre TEXT,
        released TEXT,
        updated TEXT,
        version TEXT,
        developer TEXT,
        developer_email TEXT,
        developer_website TEXT,
        content_rating TEXT,
        ad_supported INTEGER,
        offers_iap INTEGER,
        icon TEXT,
        screenshots TEXT,
        fetched_at TEXT
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id TEXT NOT NULL,
        review_id TEXT,
        user_name TEXT,
        score INTEGER,
        content TEXT,
        thumbs_up INTEGER,
        review_created_version TEXT,
        at TEXT,
        fetched_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_rev_app ON reviews(app_id, fetched_at);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_rev_unique ON reviews(app_id, review_id);

    CREATE TABLE IF NOT EXISTS surge_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_at TEXT NOT NULL,
        app_id TEXT NOT NULL,
        collection TEXT,
        category TEXT,
        surge_score REAL NOT NULL,
        signals TEXT,
        dismissed INTEGER DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()


def save_snapshot(apps: list[dict], collection: str, category: str, snapshot_at: str = None):
    if snapshot_at is None:
        snapshot_at = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    for rank, app in enumerate(apps, start=1):
        conn.execute(
            """INSERT OR REPLACE INTO snapshots
            (snapshot_at, collection, category, app_id, title, developer, score, ratings, installs, genre, rank_position, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                snapshot_at,
                collection,
                category,
                app.get("appId"),
                app.get("title"),
                app.get("developer"),
                app.get("score"),
                app.get("ratings"),
                app.get("installs"),
                app.get("genre"),
                rank,
                json.dumps(app, ensure_ascii=False),
            ),
        )
    conn.commit()
    conn.close()


def get_snapshots(collection: str, category: str, limit: int = 2):
    """Get latest N snapshots for a collection+category."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT DISTINCT snapshot_at FROM snapshots
           WHERE collection = ? AND category = ?
           ORDER BY snapshot_at DESC LIMIT ?""",
        (collection, category, limit),
    ).fetchall()
    if not rows:
        conn.close()
        return []
    times = [r["snapshot_at"] for r in rows]
    result = conn.execute(
        """SELECT * FROM snapshots
           WHERE collection = ? AND category = ? AND snapshot_at IN ({})
           ORDER BY snapshot_at DESC, rank_position ASC""".format(
            ",".join("?" * len(times))
        ),
        (collection, category, *times),
    ).fetchall()
    conn.close()
    return [dict(r) for r in result]


def save_app_detail(app: dict):
    conn = get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO app_details
        (app_id, title, description, summary, installs, score, ratings, reviews, price, free,
         genre, released, updated, version, developer, developer_email, developer_website,
         content_rating, ad_supported, offers_iap, icon, screenshots, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            app.get("appId"),
            app.get("title"),
            app.get("description"),
            app.get("summary"),
            app.get("installs"),
            app.get("score"),
            app.get("ratings"),
            app.get("reviews"),
            app.get("price"),
            1 if app.get("free") else 0,
            app.get("genre"),
            app.get("released"),
            app.get("updated"),
            app.get("version"),
            app.get("developer"),
            app.get("developerEmail"),
            app.get("developerWebsite"),
            app.get("contentRating"),
            1 if app.get("adSupported") else 0,
            1 if app.get("offersIAP") else 0,
            app.get("icon"),
            json.dumps(app.get("screenshots", [])),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def save_reviews(app_id: str, reviews: list[dict]):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    for rev in reviews:
        conn.execute(
            """INSERT INTO reviews
            (app_id, review_id, user_name, score, content, thumbs_up, review_created_version, at, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING""",
            (
                app_id,
                rev.get("id"),
                rev.get("userName"),
                rev.get("score"),
                rev.get("text"),
                rev.get("thumbsUp"),
                rev.get("version"),
                rev.get("date"),
                now,
            ),
        )
    conn.commit()
    conn.close()


def save_alert(app_id: str, collection: str, category: str, surge_score: float, signals: dict):
    conn = get_conn()
    conn.execute(
        """INSERT INTO surge_alerts (detected_at, app_id, collection, category, surge_score, signals)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            app_id,
            collection,
            category,
            surge_score,
            json.dumps(signals, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_alerts(limit: int = 50):
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM surge_alerts WHERE dismissed = 0
           ORDER BY detected_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_alerts(limit: int = 10):
    """Get highest-scoring alerts ever detected (with title and rank from latest snapshot)."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT a.*,
           (SELECT title FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as title,
           (SELECT rank_position FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as current_rank
           FROM surge_alerts a WHERE dismissed = 0
           ORDER BY a.surge_score DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_alert_count_by_category():
    """Histogram of alerts per category."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT category, COUNT(*) as cnt FROM surge_alerts
           WHERE dismissed = 0 GROUP BY category ORDER BY cnt DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_snapshot_dates():
    """Get distinct snapshot dates."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT DISTINCT snapshot_at FROM snapshots ORDER BY snapshot_at DESC"""
    ).fetchall()
    conn.close()
    return [r["snapshot_at"] for r in rows]
