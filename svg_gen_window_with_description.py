#!/usr/bin/env python3
from dataclasses import dataclass, fields
from html import escape
from typing import Iterable, Literal, Optional

HorizontalMode = Literal["even", "from_chord"]


@dataclass
class WindowSpec:
    width_mm: float
    height_mm: float
    frame_width_mm: float
    num_vertical_bars: int
    num_horizontal_bars: int  # Bars below the chord bar in "from_chord" mode.
    sash_bar_width_mm: float
    arch_height_mm: float = 0.0
    center_vertical_bar_width_mm: Optional[float] = None
    horizontal_distribution_mode: HorizontalMode = "even"
    frame_color: str = "#c7c7c7"
    glass_color: str = "#e6f2ff"
    bar_color: str = "#c7c7c7"


LABEL_FONT_SIZE_MM = 2.5
LABEL_LINE_HEIGHT_MM = 3.3
LABEL_PADDING_MM = 2.0
WINDOW_GAP_MM = 5.0


def _path_arch_outer(width: float, height: float, arch_h: float) -> str:
    return f"M 0,{arch_h} A {width / 2},{arch_h} 0 0 1 {width},{arch_h} L {width},{height} L 0,{height} Z"


def _path_arch_inner(width: float, height: float, frame_w: float, arch_h: float) -> str:
    inner_width = max(0.0, width - 2 * frame_w)
    inner_height = max(0.0, height - 2 * frame_w)
    inner_arch = max(0.0, arch_h - frame_w)
    return (f"M {frame_w},{frame_w + inner_arch} "
            f"A {inner_width / 2},{inner_arch} 0 0 1 {frame_w + inner_width},{frame_w + inner_arch} "
            f"L {frame_w + inner_width},{frame_w + inner_height} L {frame_w},{frame_w + inner_height} Z")


def _frame_rect(width: float, height: float, frame_w: float) -> str:
    return (f"M 0,0 L {width},0 L {width},{height} L 0,{height} Z "
            f"M {frame_w},{frame_w} L {width - frame_w},{frame_w} "
            f"L {width - frame_w},{height - frame_w} L {frame_w},{height - frame_w} Z")


def _values(spec: WindowSpec) -> tuple[float, float, float, int, int, float, float, str, float]:
    width, height, frame_w = float(spec.width_mm), float(spec.height_mm), float(spec.frame_width_mm)
    vertical, horizontal = int(spec.num_vertical_bars), int(spec.num_horizontal_bars)
    bar_w, arch_h = float(spec.sash_bar_width_mm), float(spec.arch_height_mm)
    centre_w = float(spec.center_vertical_bar_width_mm) if spec.center_vertical_bar_width_mm is not None else bar_w
    mode = spec.horizontal_distribution_mode
    if width <= 0 or height <= 0:
        raise ValueError("Window width and height must be positive.")
    if frame_w < 0 or 2 * frame_w >= min(width, height):
        raise ValueError("Frame width must be non-negative and less than half the window size.")
    if arch_h < 0 or arch_h > height:
        raise ValueError("Arch height must be between 0 and the total height.")
    if vertical < 0 or horizontal < 0 or bar_w < 0 or centre_w < 0:
        raise ValueError("Sash bar counts and widths cannot be negative.")
    if mode not in ("even", "from_chord"):
        raise ValueError("horizontal_distribution_mode must be 'even' or 'from_chord'.")
    return width, height, frame_w, vertical, horizontal, bar_w, arch_h, mode, centre_w


def window_spec_lines(spec: WindowSpec) -> list[str]:
    """Return every WindowSpec field formatted for the SVG label."""
    return [f"{field.name}: {getattr(spec, field.name)}" for field in fields(spec)]


def _label_width(lines: list[str]) -> float:
    return max((len(line) for line in lines), default=0) * LABEL_FONT_SIZE_MM * 0.62 + 2 * LABEL_PADDING_MM


def _window_fragment(spec: WindowSpec, x: float, y: float, cell_width: float, identifier: int) -> list[str]:
    width, height, frame_w, vertical, horizontal, bar_w, arch_h, mode, centre_w = _values(spec)
    inner_x, inner_y = frame_w, frame_w
    inner_w, inner_h = width - 2 * frame_w, height - 2 * frame_w
    window_x = x + (cell_width - width) / 2
    clip_id = f"glazingClip-{identifier}"
    if arch_h > 0:
        glazing = _path_arch_inner(width, height, frame_w, arch_h)
        frame = f"{_path_arch_outer(width, height, arch_h)} {glazing}"
        glass = f'<path d="{glazing}" fill="{escape(spec.glass_color)}" stroke="none"/>'
        clip_shape = f'<path d="{glazing}"/>'
    else:
        frame = _frame_rect(width, height, frame_w)
        glass = f'<rect x="{inner_x}" y="{inner_y}" width="{inner_w}" height="{inner_h}" fill="{escape(spec.glass_color)}" stroke="none"/>'
        clip_shape = f'<rect x="{inner_x}" y="{inner_y}" width="{inner_w}" height="{inner_h}"/>'

    out = [f'  <defs><clipPath id="{clip_id}">{clip_shape}</clipPath></defs>',
           f'  <g transform="translate({window_x},{y})">', f'    {glass}',
           f'    <path d="{frame}" fill="{escape(spec.frame_color)}" fill-rule="evenodd" stroke="none"/>',
           f'    <g clip-path="url(#{clip_id})">']
    if vertical and inner_w > 0:
        gap = inner_w / (vertical + 1)
        for index in range(vertical):
            this_width = centre_w if vertical % 2 and index == vertical // 2 else bar_w
            out.append(f'      <rect x="{inner_x + (index + 1) * gap - this_width / 2}" y="0" width="{this_width}" height="{height}" fill="{escape(spec.bar_color)}"/>')
    if inner_h > 0 and mode == "from_chord" and arch_h > 0:
        chord_y = inner_y + max(0.0, arch_h - frame_w)
        out.append(f'      <rect x="0" y="{chord_y}" width="{width}" height="{frame_w}" fill="{escape(spec.bar_color)}"/>')
        if horizontal:
            available = inner_y + inner_h - (chord_y + frame_w)
            gap = (available - horizontal * bar_w) / (horizontal + 1)
            if gap < -1e-9:
                raise ValueError("Not enough space below the chord bar to place horizontal bars.")
            for index in range(horizontal):
                out.append(f'      <rect x="0" y="{chord_y + frame_w + gap + index * (bar_w + gap)}" width="{width}" height="{bar_w}" fill="{escape(spec.bar_color)}"/>')
    elif horizontal:
        gap = inner_h / (horizontal + 1)
        for index in range(horizontal):
            out.append(f'      <rect x="0" y="{inner_y + (index + 1) * gap - bar_w / 2}" width="{width}" height="{bar_w}" fill="{escape(spec.bar_color)}"/>')
    out += ["    </g>", "  </g>"]
    text_x = x + LABEL_PADDING_MM
    text_y = y + height + LABEL_PADDING_MM + LABEL_FONT_SIZE_MM
    out.append(f'  <text x="{text_x}" y="{text_y}" font-family="monospace" font-size="{LABEL_FONT_SIZE_MM}" fill="#111">')
    for index, line in enumerate(window_spec_lines(spec)):
        out.append(f'    <tspan x="{text_x}" dy="{0 if index == 0 else LABEL_LINE_HEIGHT_MM}">{escape(line)}</tspan>')
    out.append("  </text>")
    return out


def generate_windows_svg(specs: Iterable[WindowSpec], columns: int = 1) -> str:
    """Create a non-overlapping sheet of labelled windows."""
    specs = list(specs)
    if not specs:
        raise ValueError("At least one WindowSpec is required.")
    if columns < 1:
        raise ValueError("columns must be at least 1.")
    cells = []
    for spec in specs:
        width, height, *_ = _values(spec)
        lines = window_spec_lines(spec)
        cells.append((spec, max(width + 2 * LABEL_PADDING_MM, _label_width(lines)), height + 2 * LABEL_PADDING_MM + len(lines) * LABEL_LINE_HEIGHT_MM))
    columns = min(columns, len(cells))
    col_widths = [max(cell[1] for cell in cells[col::columns]) for col in range(columns)]
    rows = [cells[index:index + columns] for index in range(0, len(cells), columns)]
    row_heights = [max(cell[2] for cell in row) for row in rows]
    total_width = sum(col_widths) + WINDOW_GAP_MM * (columns - 1)
    total_height = sum(row_heights) + WINDOW_GAP_MM * (len(rows) - 1)
    svg = ['<?xml version="1.0" encoding="UTF-8"?>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}mm" height="{total_height}mm" viewBox="0 0 {total_width} {total_height}">']
    y, identifier = 0.0, 0
    for row, row_height in zip(rows, row_heights):
        x = 0.0
        for column, (spec, _, _) in enumerate(row):
            svg.extend(_window_fragment(spec, x, y, col_widths[column], identifier))
            x += col_widths[column] + WINDOW_GAP_MM
            identifier += 1
        y += row_height + WINDOW_GAP_MM
    svg.append("</svg>")
    return "\n".join(svg)


def generate_window_svg(spec: WindowSpec) -> str:
    """Create a single-window SVG, with all WindowSpec values below it."""
    return generate_windows_svg([spec])
