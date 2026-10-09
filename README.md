# ASCII wallpaper generator

Generate PNG desktop wallpapers from an ASCII logo and a text panel. The default
is a rainbow Apple logo on black, with the reference image's five information
rows. Characters align on a monospace grid, without the reference's AI distortions.

## Generate a wallpaper

Requires Python 3.10 or later. With [uv](https://docs.astral.sh/uv/), run from this repository:

```sh
uv run ascii-wallpaper
uv run ascii-wallpaper --width 3840 --height 2160
uv run ascii-wallpaper --width 1080 --height 1920 --output output/portrait.png
uv run ascii-wallpaper --width 3440 --height 1440 --output output/ultrawide.png
```

The first command writes `output/apple-1920x1080.png`. Without `--output`, filenames
include the preset or config name and requested resolution. Parent directories
are created automatically. Output is always PNG.

You can also install the package into your Python environment:

```sh
python -m pip install .
python -m ascii_wallpaper --width 3840 --height 2160
```

The logo and text form one centered composition. Text size scales with the
shorter canvas dimension, preserving the same character grid across resolutions.
Large compositions shrink to fit within a 5% margin on each edge. Text never
wraps or truncates. Extremely small canvases still generate, but cannot show
legible characters.

```sh
uv run ascii-wallpaper --scale 1.5 --text-position left
uv run ascii-wallpaper --font /path/to/monospace.ttf
```

Scale is a positive multiplier. Fitting takes precedence when a larger scale
would exceed the margins. The font must be monospace for printable ASCII.

## Customize the logo and text

The included example uses a mountain logo, different text and colors, and puts
the text on the left:

```sh
uv run ascii-wallpaper --config examples/custom.json --output output/custom.png
```

Copy [examples/custom.json](examples/custom.json) and
[examples/mountain.txt](examples/mountain.txt) to start your own preset. All
configuration keys are optional; omitted settings use the Apple defaults.

| Key | Meaning |
| --- | --- |
| `logo_file` | ASCII `.txt` file, with spaces preserved. |
| `rows` | Ordered objects with `label`, `value`, and optional `color`. Use `[]` for logo only. |
| `palette` | Nonempty array of `#RRGGBB` colors, distributed in horizontal bands. |
| `line_colors` | Optional array with exactly one color per logo line, for precise bands. |
| `text_position` | `"left"` or `"right"`, relative to the logo. |
| `scale` | Positive size multiplier, default `1.0`. |
| `background` | Background color, default `"#000000"`. |
| `value_color` | Text value color, default `"#ffffff"`. |
| `font_path` | Optional custom monospace font file. |

Logo and font paths are resolved relative to the JSON file. CLI options override
the corresponding config values. Apple uses explicit rainbow band boundaries;
setting a new logo or palette switches to evenly distributed bands unless you
supply `line_colors`.

Logos accept printable ASCII and spaces, with no tabs. Rows accept single-line
text and retain their order. Labels receive an appended colon and align their
values in a shared column. An empty label displays just the value. All colors
must use six-digit hex notation. Unicode row text depends on the chosen font's
glyph coverage.

The values are manually supplied. Automatic system detection and image-to-ASCII
conversion are outside this first version.

## Use from Python

```python
from dataclasses import replace

from ascii_wallpaper import TextRow, apple_preset, render_wallpaper, save_wallpaper

config = replace(
    apple_preset(),
    rows=(TextRow("Project", "My workstation", "#00ffff"),),
)
save_wallpaper("output/workstation.png", width=3840, height=2160, config=config)
image = render_wallpaper(width=1920, height=1080, config=config)  # Pillow RGB image
```

`WallpaperConfig` also accepts an ASCII string directly through `logo`. Use
`load_config(path)` to load the same JSON format as the CLI.

## Development

```sh
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv build
```

The tests cover resolution and centering, proportional scaling, long-text
fitting, placement, config validation, relative asset paths, and CLI PNG output.
The rendering code has no OS-specific dependencies. Platform verification for
this initial version was performed on Linux.

The bundled DejaVu Sans Mono font makes rendering independent of installed
system fonts. Its [upstream license](https://dejavu-fonts.github.io/License.html)
is included in [FONT-LICENSE.txt](src/ascii_wallpaper/assets/FONT-LICENSE.txt).
Pillow provides text rasterization and PNG encoding.

The agreed specification is [GitHub issue #1](https://github.com/reiganarmstrong/ascii-wallpaper-generator/issues/1).
Domain terms live in [CONTEXT.md](CONTEXT.md).
