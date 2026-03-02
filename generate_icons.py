#!/usr/bin/env python

from pathlib import Path
import re


HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
LINK_TRANSFORM = "translate(8.8 5.2) scale(0.0218)"
# src: https://uxwing.com/link-hyperlink-icon/
LINK_PATH_DATA = (
    "M476.335 35.664v.001c47.554 47.552 47.552 125.365.002 172.918l-101.729 101.73"
    "c-60.027 60.025-162.073 42.413-194.762-32.45 35.888-31.191 53.387-21.102 87.58-6.638"
    " 20.128 8.512 43.74 3.955 60.08-12.387l99.375-99.371c21.49-21.493 21.492-56.662 0-78.155"
    "-21.489-21.488-56.677-21.472-78.151 0l-71.278 71.28c-23.583-11.337-50.118-14.697-75.453-10.07"
    "a121.476 121.476 0 0118.767-24.207l82.651-82.65c47.554-47.551 125.365-47.555 172.918-.001z"
    "M35.664 476.334l.001.001c47.554 47.552 125.365 47.552 172.917 0l85.682-85.682"
    "a121.496 121.496 0 0019.325-25.157c-27.876 6.951-57.764 4.015-83.932-8.805l-70.192 70.19"
    "c-21.472 21.471-56.658 21.492-78.149 0-21.492-21.491-21.493-56.658 0-78.149l99.375-99.376"
    "c20.363-20.363 61.002-26.435 91.717 1.688 29.729-3.133 41.275-8.812 59.742-26.493"
    "-39.398-69.476-137.607-80.013-194.757-22.863L35.664 303.417c-47.552 47.553-47.552 125.364 0 172.917z"
)


def parse_style(style: str) -> dict[str, str]:
    entries = {}
    for part in style.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        entries[key.strip()] = value.strip()
    return entries


def is_valid_color(color: str | None) -> bool:
    return color is not None and HEX_COLOR_RE.match(color) is not None


def color_from_reference(reference_icon: Path) -> str:
    text = reference_icon.read_text(encoding="utf-8")

    style_match = re.search(r'style="([^"]+)"', text)
    if style_match:
        style = parse_style(style_match.group(1))

        fill = style.get("fill")
        if fill != "none" and is_valid_color(fill):
            return fill

        stroke = style.get("stroke")
        if stroke != "none" and is_valid_color(stroke):
            return stroke

    for attr in ("fill", "stroke"):
        m = re.search(rf'{attr}="(#[0-9a-fA-F]{{3,8}})"', text)
        if m and is_valid_color(m.group(1)):
            return m.group(1)

    raise RuntimeError(f"Could not extract a color from '{reference_icon}'")


def get_icon_svg(color: str, direction: str) -> str:
    if direction == "forward":
        # Symmetric over the full marker height: top and bottom match marker bounds.
        # This intentionally does not align the chevron tip with the marker circle center.
        chevron = "M1.5 3.0 L6.4 10.85 L1.5 18.7"
    elif direction == "back":
        # Symmetric over the full marker height: top and bottom match marker bounds.
        # This intentionally does not align the chevron tip with the marker circle center.
        chevron = "M6.4 3.0 L1.5 10.85 L6.4 18.7"
    else:
        raise RuntimeError(f"Unknown direction: {direction}")

    return (
        f'<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <path d="{LINK_PATH_DATA}" fill="{color}" transform="{LINK_TRANSFORM}"/>\n'
        f'  <path d="{chevron}" fill="none" stroke="{color}" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"/>\n'
        "</svg>\n"
    )


def get_theme_dirs(ui_dir: Path) -> list[Path]:
    res = []
    for p in sorted(ui_dir.iterdir()):
        if not p.is_dir() or not p.name.startswith("icons"):
            continue
        ref = p / "hicolor/scalable/actions/xopp-line-style-plain.svg"
        if ref.exists():
            res.append(p)
    return res


def main() -> None:
    ui_dir = Path(__file__).resolve().parent / "ui"
    for theme_dir in get_theme_dirs(ui_dir):
        ref = theme_dir / "hicolor/scalable/actions/xopp-line-style-plain.svg"
        color = color_from_reference(ref)
        for direction in ("forward", "back"):
            icon = get_icon_svg(color, direction)
            output = theme_dir / f"hicolor/scalable/actions/xopp-navigate-{direction}.svg"
            print(f"Saving to '{output}' (color {color})")
            output.write_text(icon, encoding="utf-8")


if __name__ == "__main__":
    main()
