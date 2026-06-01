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
FETCH_NUM = 150

# Cache TTL in hours
CACHE_TTL_HOURS = 24.0

# Surge detection threshold
SURGE_THRESHOLD = 20.0
