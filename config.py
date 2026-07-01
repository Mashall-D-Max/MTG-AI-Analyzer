"""
Общие настройки проекта MTG AI Analyzer.
"""

from pathlib import Path

# ==========================================================
# Application
# ==========================================================

APP_NAME = "MTG AI Analyzer"

VERSION = "0.2.0-alpha"


# ==========================================================
# Scryfall
# ==========================================================

SCRYFALL_API = "https://api.scryfall.com"

USER_AGENT = "MTG-AI-Analyzer/0.2 " "(GitHub: Mashall-D-Max)"

REQUEST_TIMEOUT = 20

IMAGE_TIMEOUT = 30


# ==========================================================
# Cache
# ==========================================================

CACHE_DIR = Path("cache")

CARD_CACHE_DIR = CACHE_DIR / "cards"

IMAGE_CACHE_DIR = CACHE_DIR / "images"


# ==========================================================
# GUI
# ==========================================================

WINDOW_WIDTH = 1200

WINDOW_HEIGHT = 750
