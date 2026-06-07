"""
Configuration for Play Trend Hunter.
"""

# Which categories to track (subset for MVP)
# Full list available via fetch_categories()
TRACKED_CATEGORIES = [
    "GAME_ACTION",
    "GAME_ADVENTURE",
    "GAME_ARCADE",
    "GAME_PUZZLE",
    "GAME_STRATEGY",
    "GAME_SIMULATION",
    "GAME_CASUAL",
    "GAME_ROLE_PLAYING",
    "GAME_SPORTS",
    "GAME_RACING",
    "GAME_BOARD",
    "GAME_CARD",
    "GAME_WORD",
    "GAME_EDUCATIONAL",
    "GAME_MUSIC",
    "GAME_TRIVIA",
    "APPLICATION",
    "TOOLS",
    "PRODUCTIVITY",
    "COMMUNICATION",
    "SOCIAL",
    "PHOTOGRAPHY",
    "VIDEO_PLAYERS",
    "LIFESTYLE",
    "HEALTH_AND_FITNESS",
    "EDUCATION",
    "BUSINESS",
    "FINANCE",
    "ENTERTAINMENT",
    "BOOKS_AND_REFERENCE",
    "TRAVEL_AND_LOCAL",
    "SHOPPING",
    "FOOD_AND_DRINK",
    "DATING",
    "MAPS_AND_NAVIGATION",
    "AUTO_AND_VEHICLES",
    "BEAUTY",
    "ART_AND_DESIGN",
    "EVENTS",
    "HOUSE_AND_HOME",
    "LIBRARIES_AND_DEMO",
    "MEDICAL",
    "MUSIC_AND_AUDIO",
    "NEWS_AND_MAGAZINES",
    "PARENTING",
    "PERSONALIZATION",
    "WEATHER",
]

# Collections to monitor
TRACKED_COLLECTIONS = [
    "TOP_FREE",
    # "TOP_PAID",
    # "GROSSING",
]

# How many apps per list fetch
FETCH_NUM = 200

# Cache TTL in hours
# NOTE: Local PC runs once per day. TTL must be < 24h so cache is ALWAYS
# invalid on the next daily run, ensuring fresh data.
CACHE_TTL_HOURS = 20.0

# Surge detection threshold
# Calibrated weekly based on histogram analysis.
# 2026-06-04: raised from 20→30 to cut noise (49% of alerts were 20-30 range).
# 2026-06-05: raised from 30→40. Snapshot count increased 5→8, alert count
#   exploded 65→342 (Recent). Volatility filter added to surge.py.
SURGE_THRESHOLD = 40.0
