#!/usr/bin/env python3
import os
from svg_gen_window import generate_window_svg, WindowSpec

# Fassade 1 Augustiner
# Rectangular (even spacing)



def generate_svg(svg_dir: str):
    if not os.path.exists(svg_dir):
        os.makedirs(svg_dir)

    rect_svg1 = generate_window_svg(WindowSpec(
        width_mm=10, height_mm=15, frame_width_mm=1.0,
        num_vertical_bars=1, num_horizontal_bars=2,
        sash_bar_width_mm=0.8, arch_height_mm=2,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F1_10_15.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg1)

    rect_svg1_outer = generate_window_svg(WindowSpec(
        width_mm=14, height_mm=17, frame_width_mm=0.5,
        num_vertical_bars=0, num_horizontal_bars=0,
        sash_bar_width_mm=0.8, arch_height_mm=4,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F1_10_15_outer.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg1_outer)

    rect_svg2 = generate_window_svg(WindowSpec(
        width_mm=10, height_mm=20, frame_width_mm=1.0,
        num_vertical_bars=1, num_horizontal_bars=2,
        sash_bar_width_mm=0.8, arch_height_mm=2,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F2_10_20.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg2)  

    rect_svg2_outer = generate_window_svg(WindowSpec(
        width_mm=14, height_mm=22, frame_width_mm=0.5,
        num_vertical_bars=0, num_horizontal_bars=0,
        sash_bar_width_mm=0.8, arch_height_mm=4,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F2_10_20_outer.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg2_outer)  


    # Fassade 2 Augustiner
    rect_svg3 = generate_window_svg(WindowSpec(
        width_mm=9, height_mm=35, frame_width_mm=1.0,
        num_vertical_bars=1, num_horizontal_bars=6,
        sash_bar_width_mm=0.8, arch_height_mm=2,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F3_9_35.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg3)

    rect_svg3_outer = generate_window_svg(WindowSpec(
        width_mm=13, height_mm=37, frame_width_mm=0.5,
        num_vertical_bars=0, num_horizontal_bars=0,
        sash_bar_width_mm=0.8, arch_height_mm=4,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F3_9_35_outer.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg3_outer)

    # Fassade 3 Augustiner
    # Arched with: chord bar (thickness = frame width) + NH bars evenly spaced below it
    rect_svg4 = generate_window_svg(WindowSpec(
        width_mm=12, height_mm=35, frame_width_mm=1.0,
        num_vertical_bars=1, num_horizontal_bars=6,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=2,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F4_12_35.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg4)

    rect_svg4_outer = generate_window_svg(WindowSpec(
        width_mm=16, height_mm=37, frame_width_mm=0.5,
        num_vertical_bars=0, num_horizontal_bars=0,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=4,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="even"
    ))
    with open(f"{svg_dir}"+"Augustiner_F4_12_35_outer.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg4_outer)

    # Fassade 4 Augustiner
    rect_svg5 = generate_window_svg(WindowSpec(
        width_mm=10, height_mm=5, frame_width_mm=1,
        num_vertical_bars=1, num_horizontal_bars=1,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"Augustiner_F5_10_5.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg5)

    rect_svg6 = generate_window_svg(WindowSpec(
        width_mm=25, height_mm=40, frame_width_mm=1,
        num_vertical_bars=0, num_horizontal_bars=0,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=10,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"Augustiner_T25_40.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg6)

    rect_svg6_outer = generate_window_svg(WindowSpec(
        width_mm=29, height_mm=42, frame_width_mm=0.5,
        num_vertical_bars=0, num_horizontal_bars=0,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=12,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"Augustiner_T25_40_outer.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg6_outer)   

    # Augiustiner Bierhalle
    rect_svg7 = generate_window_svg(WindowSpec(
        width_mm=10, height_mm=15, frame_width_mm=1,
        num_vertical_bars=1, num_horizontal_bars=2,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F10_15.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg7)

    rect_svg8 = generate_window_svg(WindowSpec(
        width_mm=20, height_mm=20, frame_width_mm=1,
        num_vertical_bars=2, num_horizontal_bars=2,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F20_20.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg8)

    rect_svg9 = generate_window_svg(WindowSpec(
        width_mm=12, height_mm=20, frame_width_mm=1,
        num_vertical_bars=1, num_horizontal_bars=2,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F12_20.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg9)

    rect_svg10 = generate_window_svg(WindowSpec(
        width_mm=10, height_mm=20, frame_width_mm=1,
        num_vertical_bars=1, num_horizontal_bars=2,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F10_20.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg10)

    rect_svg11 = generate_window_svg(WindowSpec(
        width_mm=25, height_mm=10, frame_width_mm=1,
        num_vertical_bars=4, num_horizontal_bars=1,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F25_10.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg11)

    rect_svg12 = generate_window_svg(WindowSpec(
        width_mm=20, height_mm=10, frame_width_mm=1,
        num_vertical_bars=3, num_horizontal_bars=1,   # 4 bars below the chord bar
        sash_bar_width_mm=0.8, arch_height_mm=0,
        center_vertical_bar_width_mm=0.8,
        horizontal_distribution_mode="from_chord"
    ))
    with open(f"{svg_dir}"+"AugustinerBierhalle_F20_10.svg", "w", encoding="utf-8") as f:
        f.write(rect_svg12)

if __name__ == "__main__":
    generate_svg(svg_dir="./augustiner_svg_windows/")