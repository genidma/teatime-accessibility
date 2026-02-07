from pathlib import Path
import json

# Application metadata
APP_NAME = "teatime kcresonance"
APP_VERSION = "1.0.2"

# Configuration file for font size persistence
CONFIG_FILE = Path.home() / ".config" / "teatime_config.json"
STATS_LOG_FILE = Path.home() / ".local/share/teatime_stats.json"
DEFAULT_FONT_SCALE = 1.5
FONT_SCALE_INCREMENT = 0.1
MIN_FONT_SCALE = 0.8
MAX_FONT_SCALE = 6.0

KC_CATEGORIES = ["rdp", "fc", "g", "m", "sii", "v", "r", "b", "t", "c", "MWHH", "yss", "we", "gotb", "rf", "dw", " ", "breaks"]

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else CONFIG_FILE

    def load(self):
        """Loads configuration from the config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error decoding config file: {self.config_path}. Error: {e}")
                return {}
            except Exception as e:
                print(f"An unexpected error occurred while loading config: {e}.")
                return {}
        return {}

    def save(self, config_data):
        """Saves the configuration to the config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False


class StatsManager:
    def __init__(self, stats_path=None):
        self.stats_path = Path(stats_path) if stats_path else STATS_LOG_FILE

    def load(self):
        """Load statistics from the log file."""
        if not self.stats_path.exists():
            return []
        try:
            with open(self.stats_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading stats file: {e}")
            return []


