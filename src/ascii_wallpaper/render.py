"""Measure one composition and scale it to any canvas without reflowing the text."""

import math
from dataclasses import dataclass
from importlib.resources import files
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from .config import WallpaperConfig, apple_preset


@dataclass(frozen=True)
class _Run:
    text: str
    x: float
    y: float
    color: str


def _font(config: WallpaperConfig) -> ImageFont.FreeTypeFont:
    source = (
        Path(config.font_path).read_bytes()
        if config.font_path is not None
        else files("ascii_wallpaper").joinpath("assets/DejaVuSansMono.ttf").read_bytes()
    )
    font = ImageFont.truetype(BytesIO(source), 100, layout_engine=ImageFont.Layout.BASIC)
    widths = [font.getlength(chr(code)) for code in range(32, 127)]
    if max(widths) - min(widths) > 0.1:
        raise ValueError("Choose a monospace font so the ASCII logo stays aligned")
    return font


def _composition(config: WallpaperConfig, font: ImageFont.FreeTypeFont) -> list[_Run]:
    lines = config.logo.split("\n")
    cell = font.getlength("M")
    line_step = font.size * 1.2
    row_step = font.size * 1.8
    logo_width = max(map(len, lines)) * cell
    logo_height = (len(lines) - 1) * line_step + font.size
    labels = [f"{row.label}:" if row.label else "" for row in config.rows]
    label_width = max((font.getlength(label) for label in labels), default=0)
    value_offset = label_width + 2 * cell if label_width else 0
    panel_width = value_offset + max((font.getlength(row.value) for row in config.rows), default=0)
    panel_height = (len(config.rows) - 1) * row_step + font.size if config.rows else 0
    height = max(logo_height, panel_height)
    gap = 4 * cell if config.rows else 0
    logo_x, panel_x = 0.0, logo_width + gap
    if config.text_position == "left" and config.rows:
        panel_x, logo_x = 0.0, panel_width + gap
    runs = []
    for index, line in enumerate(lines):
        color = (
            config.line_colors[index]
            if config.line_colors is not None
            else config.palette[
                min(index * len(config.palette) // len(lines), len(config.palette) - 1)
            ]
        )
        runs.append(_Run(line, logo_x, (height - logo_height) / 2 + index * line_step, color))
    for index, (row, label) in enumerate(zip(config.rows, labels)):
        y = (height - panel_height) / 2 + index * row_step
        runs.append(_Run(label, panel_x, y, row.color))
        runs.append(_Run(row.value, panel_x + value_offset, y, config.value_color))
    return runs


def _bounds(runs: list[_Run], font: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    bounds = [(run, font.getbbox(run.text, anchor="la")) for run in runs if run.text.strip()]
    return (
        math.floor(min(run.x + box[0] for run, box in bounds)),
        math.floor(min(run.y + box[1] for run, box in bounds)),
        math.ceil(max(run.x + box[2] for run, box in bounds)),
        math.ceil(max(run.y + box[3] for run, box in bounds)),
    )


def _factor(
    width: int,
    height: int,
    config: WallpaperConfig,
    font: ImageFont.FreeTypeFont,
    bounds: tuple[int, int, int, int],
) -> float:
    left, top, right, bottom = bounds
    return min(
        min(width, height) * 0.018 / font.size * config.scale,
        width * 0.9 / (right - left),
        height * 0.9 / (bottom - top),
    )


def render_wallpaper(
    width: int = 1920,
    height: int = 1080,
    config: WallpaperConfig | None = None,
) -> Image.Image:
    """Return an RGB wallpaper at the exact requested size.

    The same character grid is retained at every resolution. Scale controls text
    size relative to the shorter canvas dimension; a 5% margin prevents clipping.
    """
    if any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in (width, height)):
        raise ValueError("Width and height must be positive integers")
    config = config if config is not None else apple_preset()
    font = _font(config)
    runs = _composition(config, font)
    bounds = _bounds(runs, font)
    factor = _factor(width, height, config, font, bounds)
    # Measure and draw with the same font. A design size of at least 100 gives
    # small output text a clean downsample; larger canvases get at least 2x text.
    font = font.font_variant(size=max(100, math.ceil(font.size * factor * 2)))
    runs = _composition(config, font)
    bounds = _bounds(runs, font)
    factor = _factor(width, height, config, font, bounds)
    left, top, right, bottom = bounds
    block_width, block_height = right - left, bottom - top
    # Supersample only the content, rather than the entire black background.
    tile_width = max(1, round(block_width * factor))
    tile_height = max(1, round(block_height * factor))
    tile = Image.new("RGB", (block_width, block_height), config.background)
    draw = ImageDraw.Draw(tile)
    for run in runs:
        draw.text(
            (run.x - left, run.y - top),
            run.text,
            fill=run.color,
            font=font,
            anchor="la",
        )
    tile = tile.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
    # Font advance boxes include side bearings. Center the visible composition
    # after resampling so those bearings do not shift it to one side.
    ink = ImageChops.difference(tile, Image.new("RGB", tile.size, config.background)).getbbox()
    if ink is not None:
        tile = tile.crop(ink)
        tile_width, tile_height = tile.size
    image = Image.new("RGB", (width, height), config.background)
    image.paste(tile, ((width - tile_width) // 2, (height - tile_height) // 2))
    return image


def save_wallpaper(
    path: str | Path,
    width: int = 1920,
    height: int = 1080,
    config: WallpaperConfig | None = None,
) -> Path:
    """Render and save a PNG, creating its parent directory if necessary."""
    path = Path(path)
    image = render_wallpaper(width, height, config)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    return path
