#!/usr/bin/env python3
"""
Create README images under assets/repo_preview_images/.

  python scripts/generate_readme_assets.py
      Pillow-only marketing stills (no API key).

  python scripts/generate_readme_assets.py --from-pipeline
      Runs the full OpenAI pipeline (needs OPENAI_API_KEY or .env), then
      copies preview_composite.png and builds a layered-stack still from PNGs.

Load order for keys: optional python-dotenv (.env), then process environment.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ASSETS = ROOT / "assets" / "repo_preview_images"
OUT = ROOT / "output_card"


def _bootstrap_path() -> None:
    if SRC.is_dir() and str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return
    env_path = ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path)


def _ensure_assets_dir() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)


def build_local_marketing_images() -> None:
    """Deterministic Pillow art for README when no API run is requested."""
    from PIL import Image, ImageDraw, ImageFont

    _ensure_assets_dir()

    def font(sz: int, bold: bool = False) -> ImageFont.ImageFont:
        candidates = (
            ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"]
            if bold
            else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
        )
        for p in candidates:
            if Path(p).exists():
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    # --- Flat preview style ---
    w, h = 480, 720
    flat = Image.new("RGB", (w, h), (12, 14, 28))
    dr = ImageDraw.Draw(flat)
    for i in range(h):
        t = i / h
        c = (
            int(24 + 40 * t),
            int(18 + 30 * t),
            int(48 + 80 * t),
        )
        dr.line([(0, i), (w, i)], fill=c)
    margin = 28
    dr.rounded_rectangle(
        (margin, margin, w - margin, h - margin),
        radius=28,
        outline=(255, 255, 255, 40),
        width=3,
    )
    dr.rounded_rectangle(
        (margin + 10, margin + 10, w - margin - 10, int(h * 0.42)),
        radius=22,
        fill=(30, 36, 70, 200),
    )
    f_title = font(34, bold=True)
    f_sub = font(20)
    f_small = font(16)
    dr.text((52, 52), "4D Card Generator", font=f_title, fill=(245, 247, 255))
    dr.text((54, 98), "Flat preview (preview_composite.png)", font=f_sub, fill=(190, 205, 255))
    dr.text((52, int(h * 0.48)), "Stacked layers → one quick composite for inspection.", font=f_small, fill=(200, 210, 235))
    dr.text((52, int(h * 0.52)), "The HTML viewer uses each PNG separately.", font=f_small, fill=(200, 210, 235))
    strip_y = h - 120
    dr.rounded_rectangle((40, strip_y, w - 40, h - 36), radius=18, fill=(16, 18, 32, 230), outline=(255, 255, 255, 55), width=2)
    dr.text((56, strip_y + 18), "HP 280   •   Photon Slash   •   Nova Spiral", font=f_small, fill=(235, 238, 255))
    flat.save(ASSETS / "preview_flat.png", format="PNG", optimize=True)

    # --- Parallax / layered concept ---
    pv = Image.new("RGB", (w, h), (8, 10, 22))
    drp = ImageDraw.Draw(pv)
    for i in range(h):
        a = 0.5 + 0.5 * math.sin(i * 0.02)
        drp.line([(0, i), (w, i)], fill=(int(20 + 25 * a), int(12 + 20 * a), int(40 + 50 * a)))
    drp.text((44, 36), "Layered viewer (parallax)", font=f_title, fill=(245, 247, 255))
    drp.text((46, 86), "Each PNG = its own depth plane", font=f_sub, fill=(190, 205, 255))

    layers = [
        ("background.png", -38, 0.22, (60, 70, 120)),
        ("holo_overlay.png", -22, 0.26, (120, 90, 200)),
        ("fx_back.png", -8, 0.30, (90, 140, 220)),
        ("player.png", 8, 0.34, (220, 200, 255)),
        ("fx_front.png", 24, 0.38, (255, 220, 180)),
        ("ui_overlay.png", 40, 0.42, (240, 245, 255)),
        ("gloss_overlay.png", 54, 0.46, (255, 255, 255)),
    ]
    cx, cy = w // 2, int(h * 0.58)
    for name, dx, scale, fill in layers:
        rw = int(w * 0.62 * scale)
        rh = int(h * 0.5 * scale)
        x0 = cx - rw // 2 + dx
        y0 = cy - rh // 2 - int(dx * 0.35)
        drp.rounded_rectangle((x0, y0, x0 + rw, y0 + rh), radius=16, fill=fill, outline=(255, 255, 255, 90), width=2)
        drp.text((x0 + 14, y0 + rh // 2 - 10), name, font=f_small, fill=(18, 18, 28))

    pv.save(ASSETS / "viewer_parallax.png", format="PNG", optimize=True)

    # --- Output folder strip ---
    bw, bh = 920, 260
    banner = Image.new("RGB", (bw, bh), (18, 20, 32))
    db = ImageDraw.Draw(banner)
    for i in range(bh):
        db.line([(0, i), (bw, i)], fill=(int(22 + 8 * (i / bh)), int(20 + 6 * (i / bh)), int(36 + 12 * (i / bh))))
    db.text((36, 28), "output_card/ (example layout)", font=font(28, bold=True), fill=(245, 247, 255))
    lines = [
        "character_reference.png   background.png   player.png   player_raw.png",
        "fx_back.png   fx_front.png   ui_overlay.png   holo_overlay.png   gloss_overlay.png",
        "preview_composite.png   viewer.html   manifest.json   scene_manifest.json   style_bible.json",
    ]
    y = 78
    mono = font(17)
    for line in lines:
        db.text((40, y), line, font=mono, fill=(200, 215, 255))
        y += 34
    db.text((40, bh - 52), "Run:  python scripts/generate_readme_assets.py --from-pipeline  (with OPENAI_API_KEY)", font=f_small, fill=(160, 175, 210))
    banner.save(ASSETS / "output_folder.png", format="PNG", optimize=True)

    print(f"Wrote local marketing PNGs to {ASSETS}")


def build_from_pipeline() -> None:
    _load_dotenv()
    _bootstrap_path()
    _ensure_assets_dir()

    from PIL import Image, ImageDraw, ImageFont

    from fourd_card.config import default_runtime_config  # type: ignore
    from fourd_card.pipeline import run_full_pipeline  # type: ignore

    cfg = default_runtime_config(output_dir=OUT, card_override=None)
    print("Running full OpenAI pipeline (this may take several minutes)...")
    run_full_pipeline(cfg, overwrite=True)

    preview = OUT / "preview_composite.png"
    if not preview.is_file():
        raise RuntimeError("Pipeline finished but preview_composite.png is missing.")
    import shutil

    shutil.copy(preview, ASSETS / "preview_flat.png")
    print(f"Copied pipeline preview -> {ASSETS / 'preview_flat.png'}")

    # Stack still from real layers (subtle offsets)
    layer_files = [
        OUT / "background.png",
        OUT / "holo_overlay.png",
        OUT / "fx_back.png",
        OUT / "player.png",
        OUT / "fx_front.png",
        OUT / "ui_overlay.png",
        OUT / "gloss_overlay.png",
    ]
    cw, ch = 480, 720
    canvas = Image.new("RGBA", (cw, ch), (10, 12, 26, 255))
    for i, path in enumerate(layer_files):
        if not path.is_file():
            continue
        im = Image.open(path).convert("RGBA").resize((cw, ch), Image.LANCZOS)
        dx, dy = int((i - 3) * 6), int((i - 3) * 5)
        layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        layer.paste(im, (dx, dy), im)
        canvas = Image.alpha_composite(canvas, layer)
    canvas = canvas.convert("RGB")
    canvas.save(ASSETS / "viewer_parallax.png", format="PNG", optimize=True)
    print(f"Wrote layered stack still -> {ASSETS / 'viewer_parallax.png'}")

    # Folder banner from real manifest names
    mono_path = "C:/Windows/Fonts/consola.ttf"
    try:
        mono = ImageFont.truetype(mono_path, 16) if Path(mono_path).exists() else ImageFont.load_default()
    except OSError:
        mono = ImageFont.load_default()
    def _title_font(sz: int) -> ImageFont.ImageFont:
        for p in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"):
            if Path(p).exists():
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    bw, bh = 920, 260
    banner = Image.new("RGB", (bw, bh), (14, 16, 28))
    db = ImageDraw.Draw(banner)
    db.text((32, 24), "output_card/ (from your run)", font=_title_font(26), fill=(245, 247, 255))
    y = 56
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            db.text((40, y), p.name, font=mono, fill=(200, 215, 255))
            y += 22
            if y > bh - 40:
                db.text((40, y), "…", font=mono, fill=(200, 215, 255))
                break
    banner.save(ASSETS / "output_folder.png", format="PNG", optimize=True)
    print(f"Wrote folder listing -> {ASSETS / 'output_folder.png'}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate README images for the repo.")
    ap.add_argument(
        "--from-pipeline",
        action="store_true",
        help="Run OpenAI pipeline then rebuild README assets from output_card/.",
    )
    args = ap.parse_args()
    try:
        if args.from_pipeline:
            build_from_pipeline()
        else:
            build_local_marketing_images()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
