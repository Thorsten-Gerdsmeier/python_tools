#!/usr/bin/env python3
"""Generate the Augustiner window SVG files from one list of specifications."""
import argparse
from pathlib import Path

from svg_gen_window_with_description import WindowSpec, generate_window_svg, generate_windows_svg


# Add or change windows here.  Output filenames are derived from these values.
WINDOW_SPECS: list[WindowSpec] = [
    WindowSpec(10, 15, 1.0, 1, 2, 0.8, arch_height_mm=2, center_vertical_bar_width_mm=0.8),
    WindowSpec(14, 17, 0.5, 0, 0, 0.8, arch_height_mm=4, center_vertical_bar_width_mm=0.8),
    WindowSpec(10, 20, 1.0, 1, 2, 0.8, arch_height_mm=2, center_vertical_bar_width_mm=0.8),
    WindowSpec(14, 22, 0.5, 0, 0, 0.8, arch_height_mm=4, center_vertical_bar_width_mm=0.8),
    WindowSpec(9, 35, 1.0, 1, 6, 0.8, arch_height_mm=2, center_vertical_bar_width_mm=0.8),
    WindowSpec(13, 37, 0.5, 0, 0, 0.8, arch_height_mm=4, center_vertical_bar_width_mm=0.8),
    WindowSpec(12, 35, 1.0, 1, 6, 0.8, arch_height_mm=2, center_vertical_bar_width_mm=0.8),
    WindowSpec(16, 37, 0.5, 0, 0, 0.8, arch_height_mm=4, center_vertical_bar_width_mm=0.8),
    WindowSpec(10, 5, 1, 1, 1, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(25, 40, 1, 0, 0, 0.8, arch_height_mm=10, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(29, 42, 0.5, 0, 0, 0.8, arch_height_mm=12, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(10, 15, 1, 1, 2, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(20, 20, 1, 2, 2, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(12, 20, 1, 1, 2, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(10, 20, 1, 1, 2, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(25, 10, 1, 4, 1, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
    WindowSpec(20, 10, 1, 3, 1, 0.8, center_vertical_bar_width_mm=0.8, horizontal_distribution_mode="from_chord"),
]


def _number(value: float) -> str:
    """Format a dimension safely and without unnecessary trailing zeroes."""
    return f"{value:g}".replace("-", "neg").replace(".", "p")


def filename_for(spec: WindowSpec, index: int) -> str:
    """Return a unique, descriptive filename derived from a WindowSpec."""
    return (
        f"window_{index:02d}_"
        f"{_number(spec.width_mm)}x{_number(spec.height_mm)}mm_"
        f"frame-{_number(spec.frame_width_mm)}_"
        f"arch-{_number(spec.arch_height_mm)}_"
        f"v-{spec.num_vertical_bars}_h-{spec.num_horizontal_bars}_"
        f"{spec.horizontal_distribution_mode}.svg"
    )


def generate_svg(svg_dir: str, write_combined: bool = False, columns: int = 3) -> list[Path]:
    """Generate one labelled SVG per WindowSpec and return their paths."""
    output_dir = Path(svg_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, spec in enumerate(WINDOW_SPECS, start=1):
        output_path = output_dir / filename_for(spec, index)
        output_path.write_text(generate_window_svg(spec), encoding="utf-8")
        paths.append(output_path)

    if write_combined:
        combined_path = output_dir / "all_windows.svg"
        combined_path.write_text(generate_windows_svg(WINDOW_SPECS, columns=columns), encoding="utf-8")
        paths.append(combined_path)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Augustiner window SVGs.")
    parser.add_argument("--svg-dir", default="./augustiner_svg_windows/", help="Output directory.")
    parser.add_argument("--combined", action="store_true", help="Also generate all_windows.svg.")
    parser.add_argument("--columns", type=int, default=3, help="Columns in all_windows.svg (default: 3).")
    args = parser.parse_args()
    generate_svg(args.svg_dir, write_combined=args.combined, columns=args.columns)
