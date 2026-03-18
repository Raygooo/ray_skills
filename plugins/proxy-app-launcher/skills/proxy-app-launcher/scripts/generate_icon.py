#!/usr/bin/env python3
"""Generate a proxy-badged icon from an existing macOS .icns file.

Extracts the source icon, adds a blue lightning badge in the bottom-right,
and produces a new .icns file via iconutil.

Usage:
    python generate_icon.py --source /path/to/original.icns --output /path/to/new.icns
"""

import argparse
import os
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description="Add proxy badge to macOS app icon")
    parser.add_argument("--source", required=True, help="Path to source .icns file")
    parser.add_argument("--output", required=True, help="Path for output .icns file")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: source icon not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    tmp_dir = tempfile.mkdtemp(prefix="proxy-icon-")

    # Extract PNG from icns using sips
    png_path = os.path.join(tmp_dir, "original.png")
    subprocess.run(
        ["sips", "-s", "format", "png", args.source, "--out", png_path],
        capture_output=True,
        check=True,
    )

    # Open and add badge
    img = Image.open(png_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = img.size
    badge_size = int(w * 0.32)
    margin = int(w * 0.05)
    x0 = w - badge_size - margin
    y0 = h - badge_size - margin
    x1 = x0 + badge_size
    y1 = y0 + badge_size

    # Blue circle background
    draw.ellipse([x0, y0, x1, y1], fill=(59, 130, 246, 240))
    # White border
    draw.ellipse([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=(255, 255, 255, 200), width=8)

    # Lightning bolt
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    r = badge_size / 2
    bolt = [
        (cx - r * 0.12, cy - r * 0.55),
        (cx + r * 0.25, cy + r * 0.05),
        (cx - r * 0.02, cy + r * 0.05),
        (cx + r * 0.12, cy + r * 0.55),
        (cx - r * 0.25, cy - r * 0.05),
        (cx + r * 0.02, cy - r * 0.05),
    ]
    draw.polygon(bolt, fill=(255, 255, 255, 255))

    result = Image.alpha_composite(img, overlay)

    # Build iconset
    iconset = os.path.join(tmp_dir, "icon.iconset")
    os.makedirs(iconset)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        resized = result.resize((s, s), Image.LANCZOS)
        resized.save(os.path.join(iconset, f"icon_{s}x{s}.png"))
        if s <= 512:
            resized2 = result.resize((s * 2, s * 2), Image.LANCZOS)
            resized2.save(os.path.join(iconset, f"icon_{s}x{s}@2x.png"))

    # Convert to icns
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    r = subprocess.run(
        ["iconutil", "-c", "icns", iconset, "-o", args.output],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(f"iconutil error: {r.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {args.output} ({os.path.getsize(args.output)} bytes)")


if __name__ == "__main__":
    main()
