"""Teatime package exports."""

from .core import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_FONT_SCALE,
    CONFIG_DIR,
    CONFIG_FILE,
    DATA_DIR,
    STATS_LOG_FILE,
    FONT_SCALE_INCREMENT,
    MIN_FONT_SCALE,
    MAX_FONT_SCALE,
)
from .app import TeaTimerApp, main

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_FONT_SCALE",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "DATA_DIR",
    "STATS_LOG_FILE",
    "FONT_SCALE_INCREMENT",
    "MIN_FONT_SCALE",
    "MAX_FONT_SCALE",
    "TeaTimerApp",
    "main",
]
