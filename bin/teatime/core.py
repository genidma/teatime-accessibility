from pathlib import Path

# Application metadata
APP_NAME = "TeaTime Accessibility - Photosensitive version"
APP_VERSION = "v1.3.6-photosensitive"
DEFAULT_FONT_SCALE = 1.0
CONFIG_DIR = Path.home() / ".config" / "teatime"
CONFIG_FILE = CONFIG_DIR / "settings.json"
DATA_DIR = Path.home() / ".local" / "share"
STATS_LOG_FILE = DATA_DIR / "teatime_stats.json"
# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

