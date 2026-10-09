import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from ascii_wallpaper import TextRow, WallpaperConfig, apple_preset, load_config, render_wallpaper

ROOT = Path(__file__).resolve().parents[1]


def ink_bounds(image):
    background = Image.new("RGB", image.size, "black")
    return ImageChops.difference(image, background).getbbox()


@pytest.mark.parametrize("size", [(1920, 1080), (3840, 2160), (1080, 1920), (3440, 1440)])
def test_wallpaper_fits_and_centers_at_desktop_aspect_ratios(size):
    image = render_wallpaper(*size)
    assert image.size == size
    assert image.mode == "RGB"
    assert image.getpixel((0, 0)) == (0, 0, 0)
    left, top, right, bottom = ink_bounds(image)
    assert left >= size[0] * 0.05 - 1
    assert top >= size[1] * 0.05 - 1
    assert right <= size[0] * 0.95 + 1
    assert bottom <= size[1] * 0.95 + 1
    assert abs(left - (size[0] - right)) <= 2
    assert abs(top - (size[1] - bottom)) <= 2


def test_4k_doubles_the_composition_without_changing_the_character_grid():
    small = ink_bounds(render_wallpaper(1920, 1080))
    large = ink_bounds(render_wallpaper(3840, 2160))
    # Antialiased edge pixels round differently at each resolution.
    assert (large[2] - large[0]) / (small[2] - small[0]) == pytest.approx(2, abs=0.01)
    assert (large[3] - large[1]) / (small[3] - small[1]) == pytest.approx(2, abs=0.01)


def test_long_text_and_large_scale_fit_instead_of_clipping():
    config = replace(apple_preset(), rows=(TextRow("Note", "M" * 200),), scale=100)
    image = render_wallpaper(600, 900, config)
    left, top, right, bottom = ink_bounds(image)
    assert 29 <= left < right <= 571
    assert 44 <= top < bottom <= 856


def test_text_position_moves_the_colored_logo_to_the_other_side():
    config = WallpaperConfig(logo="MMMM\nMMMM", palette=("#00ff00",), rows=(TextRow("", "WWW"),))
    for position in ("left", "right"):
        image = render_wallpaper(800, 400, replace(config, text_position=position, scale=4))
        pixels = image.load()
        green_x = [
            x
            for x in range(image.width)
            for y in range(image.height)
            if pixels[x, y][1] > 150 and pixels[x, y][0] < 30
        ]
        assert green_x
        if position == "right":
            assert max(green_x) < image.width / 2
        else:
            assert min(green_x) > image.width / 2


def test_config_assets_are_relative_to_the_config_file(tmp_path, monkeypatch):
    (tmp_path / "logo.txt").write_text("  /\\\n /MM\\\n", encoding="utf-8")
    path = tmp_path / "custom.json"
    path.write_text(
        json.dumps(
            {
                "logo_file": "logo.txt",
                "palette": ["#00ffff"],
                "rows": [{"label": "Name", "value": "Example"}],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(ROOT)
    config = load_config(path)
    assert config.logo.startswith("  /\\")
    assert config.line_colors is None
    assert ink_bounds(render_wallpaper(500, 500, config)) is not None


@pytest.mark.parametrize(
    "data",
    [
        {"scale": 0},
        {"scale": float("nan")},
        {"text_position": "above"},
        {"palette": []},
        {"palette": ["oops"]},
        {"rowz": []},
        {"rows": [{"label": "OS"}]},
        {"rows": [{"label": "OS", "value": 123}]},
        {"rows": [{"label": "OS", "value": "a\nb"}]},
        {"line_colors": ["#ff0000"]},
        {"logo_file": None},
    ],
)
def test_invalid_configuration_is_rejected_with_a_useful_error(tmp_path, data):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)


@pytest.mark.parametrize("logo", ["", "   ", "\tM", "\u2603", "M\rM"])
def test_logo_must_be_printable_ascii_with_preserved_spaces(logo):
    with pytest.raises(ValueError):
        WallpaperConfig(logo=logo)


def test_empty_text_panel_and_tiny_canvas_are_supported():
    config = WallpaperConfig(rows=())
    assert ink_bounds(render_wallpaper(300, 300, config)) is not None
    assert render_wallpaper(1, 1, config).size == (1, 1)


def test_cli_saves_custom_png_and_reports_invalid_dimensions(tmp_path):
    output = tmp_path / "nested" / "custom.png"
    success = subprocess.run(
        [
            sys.executable,
            "-m",
            "ascii_wallpaper",
            "--config",
            str(ROOT / "examples/custom.json"),
            "--width",
            "640",
            "--height",
            "480",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert success.returncode == 0, success.stderr
    with Image.open(output) as image:
        assert image.format == "PNG"
        assert image.size == (640, 480)
    failure = subprocess.run(
        [
            sys.executable,
            "-m",
            "ascii_wallpaper",
            "--width",
            "0",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert failure.returncode == 2
    assert "positive integers" in failure.stderr
    assert "Traceback" not in failure.stderr
