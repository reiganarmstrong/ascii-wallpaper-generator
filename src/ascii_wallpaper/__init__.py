"""ASCII wallpaper generator's public Python interface."""

from .config import TextRow, WallpaperConfig, apple_preset, load_config
from .render import render_wallpaper, save_wallpaper

__all__ = [
    "TextRow",
    "WallpaperConfig",
    "apple_preset",
    "load_config",
    "render_wallpaper",
    "save_wallpaper",
]
