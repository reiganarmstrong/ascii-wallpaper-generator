"""Wallpaper data and the optional JSON configuration file."""

import json
import math
import re
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

RAINBOW = ("#00ff00", "#ffff00", "#ff9900", "#ff0055", "#ff00ff", "#00dfff")


def _color(value: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("Colors must be six-digit hex strings, such as #00ff00")


def _single_line(value: str, name: str) -> None:
    if not isinstance(value, str) or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f"{name} must be a string without tabs, newlines, or control characters")


@dataclass(frozen=True)
class TextRow:
    label: str
    value: str
    color: str = "#ffffff"

    def __post_init__(self) -> None:
        _single_line(self.label, "Row label")
        _single_line(self.value, "Row value")
        _color(self.color)


def _apple() -> str:
    return files("ascii_wallpaper").joinpath("assets/apple.txt").read_text(encoding="utf-8")


def _rows() -> tuple[TextRow, ...]:
    return (
        TextRow("OS", "macOS", "#00ff00"),
        TextRow("Model", "MacBook Pro 14-inch", "#ffff00"),
        TextRow("Chip", "Apple M1 Pro", "#ff0055"),
        TextRow("Memory", "16 GB", "#ff00ff"),
        TextRow("Storage", "512 GB SSD", "#00ffff"),
    )


@dataclass(frozen=True)
class WallpaperConfig:
    logo: str = field(default_factory=_apple)
    rows: tuple[TextRow, ...] = field(default_factory=_rows)
    palette: tuple[str, ...] = RAINBOW
    # Optional one color per logo line for precise band boundaries.
    line_colors: tuple[str, ...] | None = None
    text_position: str = "right"
    scale: float = 1.0
    background: str = "#000000"
    value_color: str = "#ffffff"
    font_path: Path | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.logo, str):
            raise TypeError("Logo must be ASCII text")
        # Normalize file line endings; preserve spaces and intentionally blank interior lines.
        logo = self.logo.replace("\r\n", "\n").rstrip("\n")
        if not logo.strip() or any(c != "\n" and not 32 <= ord(c) <= 126 for c in logo):
            raise ValueError(
                "Logo must contain printable ASCII characters and spaces, without tabs"
            )
        object.__setattr__(self, "logo", logo)
        if not isinstance(self.rows, (tuple, list)) or not all(
            isinstance(row, TextRow) for row in self.rows
        ):
            raise ValueError("Rows must be a sequence of TextRow objects")
        object.__setattr__(self, "rows", tuple(self.rows))
        if not isinstance(self.palette, (tuple, list)) or not self.palette:
            raise ValueError("Palette must be a nonempty sequence of colors")
        for color in self.palette:
            _color(color)
        object.__setattr__(self, "palette", tuple(self.palette))
        if self.line_colors is not None:
            if not isinstance(self.line_colors, (tuple, list)) or len(self.line_colors) != len(
                logo.split("\n")
            ):
                raise ValueError("line_colors must contain exactly one color per logo line")
            for color in self.line_colors:
                _color(color)
            object.__setattr__(self, "line_colors", tuple(self.line_colors))
        if self.text_position not in ("left", "right"):
            raise ValueError("text_position must be left or right")
        if (
            isinstance(self.scale, bool)
            or not isinstance(self.scale, (int, float))
            or not math.isfinite(self.scale)
            or self.scale <= 0
        ):
            raise ValueError("Scale must be a finite positive number")
        _color(self.background)
        _color(self.value_color)


def apple_preset() -> WallpaperConfig:
    """Return the reference-inspired Apple wallpaper, with explicit rainbow bands."""
    colors = [RAINBOW[0]] * 5 + [RAINBOW[1]] * 2 + [RAINBOW[2]] * 2
    colors += [RAINBOW[3]] * 2 + [RAINBOW[4]] * 2 + [RAINBOW[5]] * 4
    return WallpaperConfig(line_colors=tuple(colors))


def load_config(path: str | Path) -> WallpaperConfig:
    """Load a JSON config. Logo and font paths are relative to the config file."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    allowed = {
        "logo_file",
        "rows",
        "palette",
        "line_colors",
        "text_position",
        "scale",
        "background",
        "value_color",
        "font_path",
    }
    if not isinstance(data, dict):
        raise TypeError("Configuration must be a JSON object")
    if unknown := data.keys() - allowed:
        raise ValueError(f"Unknown configuration keys: {', '.join(sorted(unknown))}")
    defaults = apple_preset()
    values = dict(data)
    for name in ("logo_file", "font_path"):
        if name in values and not isinstance(values[name], str):
            raise ValueError(f"{name} must be a path string")
    if "logo_file" in values:
        values["logo"] = (path.parent / values.pop("logo_file")).read_text(encoding="utf-8")
    if "font_path" in values:
        values["font_path"] = path.parent / values["font_path"]
    if "rows" in values:
        if not isinstance(values["rows"], list):
            raise ValueError("rows must be an array of label/value objects")
        rows = []
        for row in values["rows"]:
            if not isinstance(row, dict) or not {"label", "value"} <= row.keys():
                raise ValueError("Each row must contain label and value")
            if row.keys() - {"label", "value", "color"}:
                raise ValueError("Rows support only label, value, and color")
            rows.append(TextRow(**row))
        values["rows"] = tuple(rows)
    # Preserve Apple's exact bands unless a custom logo or palette replaces them.
    if not {"logo", "palette", "line_colors"} & values.keys():
        values["line_colors"] = defaults.line_colors
    return WallpaperConfig(**values)
