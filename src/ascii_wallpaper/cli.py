"""Command-line entry point."""

import argparse
from dataclasses import replace
from pathlib import Path

from .config import apple_preset, load_config
from .render import save_wallpaper


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a colorful ASCII wallpaper as a PNG.")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("-o", "--output", type=Path, help="Output PNG path")
    parser.add_argument(
        "--config", type=Path, help="JSON config; relative asset paths use its folder"
    )
    parser.add_argument(
        "--scale", type=float, help="Content size multiplier, fitted within the canvas"
    )
    parser.add_argument("--text-position", choices=("left", "right"))
    parser.add_argument("--font", type=Path, help="Custom monospace TrueType/OpenType font")
    args = parser.parse_args()
    try:
        config = load_config(args.config) if args.config else apple_preset()
        changes = {}
        for name in ("scale", "text_position"):
            if getattr(args, name) is not None:
                changes[name] = getattr(args, name)
        if args.font is not None:
            changes["font_path"] = args.font
        config = replace(config, **changes)
        name = args.config.stem if args.config else "apple"
        path = args.output or Path("output") / f"{name}-{args.width}x{args.height}.png"
        output = save_wallpaper(path, args.width, args.height, config)
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(f"Saved {args.width}x{args.height} PNG to {output}")
