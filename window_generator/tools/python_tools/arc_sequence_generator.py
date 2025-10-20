#!/usr/bin/env python3
"""
Arc-shape SVG generator

Pattern:
  [ U -> semicircle ] * n_semicircles  -> final U
With end caps:
  - Leftmost U's left vertical is extended upward above the semicircle apex
  - Final U's right vertical is extended upward by the same amount
  - A horizontal line connects the top of these two extensions

All geometry is parameterized. Output is a single continuous SVG path.
"""

from pathlib import Path

def arc_shape_svg(
    n_semicircles: int,
    R: float = 24.0,          # radius of each semicircle
    u_width: float = 16.0,    # horizontal span of each U-shape
    u_depth: float = 28.0,    # depth of each U-shape (vertical)
    ext_above: float = 12.0,  # how far ABOVE the semicircle apex the end extensions go
    stroke: str = "black",
    stroke_width: float = 2.5,
    margin: float = 16.0,
    linecap: str = "round",
    linejoin: str = "round",
    background: str = "white",
) -> str:
    """
    Build the alternating pattern:
      [U -> semicircle] * n_semicircles  -> final U
    With equal vertical extensions at both ends, connected by a top line.

    Returns:
        SVG string.
    """
    assert n_semicircles >= 1, "n_semicircles must be >= 1"
    assert ext_above > 0, "ext_above must be > 0"

    # Positioning:
    # Baseline is where U's top and semicircle endpoints lie.
    # The semicircle apex is at (baseline - R).
    # We set top_y such that the extensions reach 'ext_above' above the apex.
    top_y = margin
    baseline = top_y + R + ext_above  # ensures extensions reach above apex
    arc_apex_y = baseline - R
    assert top_y < arc_apex_y, "Increase ext_above or margin to rise above the arc apex."

    # Total width:
    # Each repetition contributes (u_width + 2R); after n reps we add the final U width.
    pattern_width = n_semicircles * (u_width + 2 * R) + u_width
    total_width = pattern_width + 2 * margin
    # Total height: top to the deepest U plus a bottom margin
    total_height = baseline + u_depth + margin

    x = margin
    cmds = []

    # Start at left baseline
    cmds.append(f"M {x:.2f},{baseline:.2f}")

    # LEFT vertical extension (up above apex), then back to baseline (so it remains the U's left leg)
    cmds.append(f"V {top_y:.2f}")
    cmds.append(f"V {baseline:.2f}")

    # Repeating [U -> semicircle]
    for _ in range(n_semicircles):
        # U: down, right, up
        cmds.append(f"V {baseline + u_depth:.2f}")  # down
        x += u_width
        cmds.append(f"H {x:.2f}")                   # right
        cmds.append(f"V {baseline:.2f}")            # up

        # Semicircle to the right, bulging upward
        x_arc_end = x + 2 * R
        # Arc: rx ry  rotation large-arc-flag sweep-flag  x y
        # For a half-circle upward from left to right: large-arc=0, sweep=1 works here.
        cmds.append(f"A {R:.2f},{R:.2f} 0 0 1 {x_arc_end:.2f},{baseline:.2f}")
        x = x_arc_end

    # Final U
    cmds.append(f"V {baseline + u_depth:.2f}")
    x += u_width
    cmds.append(f"H {x:.2f}")
    cmds.append(f"V {baseline:.2f}")

    # RIGHT vertical extension up
    cmds.append(f"V {top_y:.2f}")

    # Connect the top of the right extension back to the top of the left extension
    left_x = margin
    cmds.append(f"H {left_x:.2f}")

    path_d = " ".join(cmds)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{total_width:.0f}" height="{total_height:.0f}"
     viewBox="0 0 {total_width:.0f} {total_height:.0f}">
  <rect x="0" y="0" width="{total_width:.0f}" height="{total_height:.0f}" fill="{background}"/>
  <path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}"
        stroke-linecap="{linecap}" stroke-linejoin="{linejoin}"/>
</svg>"""
    return svg


# --- Example usage / CLI-ish entry point ---
if __name__ == "__main__":
    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Tweak parameters here if desired
    examples = [
        ("arc_out_1.svg", 1),
        ("arc_out_3.svg", 3),
        ("arc_out_6.svg", 6),
    ]

    for fname, n in examples:
        content = arc_shape_svg(
            n_semicircles=n,
            R=24.0,
            u_width=18.0,
            u_depth=30.0,
            ext_above=14.0,  # how far above the arc apex the end extensions go
            stroke="black",
            stroke_width=2.5,
            margin=20.0,
        )
        (out_dir / fname).write_text(content, encoding="utf-8")
        print(f"Wrote {fname}")