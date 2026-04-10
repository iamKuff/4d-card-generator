from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from .config import (
    CANVAS_SIZE,
    IMAGE_MODEL,
    IMAGE_QUALITY,
    IMAGE_SIZE,
    TEXT_MODEL,
    default_runtime_config,
    load_card_config_from_json,
)
from .pipeline import rebuild_overlays_preview_manifests, rebuild_viewer_and_manifests, run_full_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate layered 4D anime-style player cards (PNG layers + HTML viewer).",
    )
    p.add_argument(
        "--config",
        type=Path,
        default=None,
        help="JSON card config (see examples/sample_config.json).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: ./output_card).",
    )
    p.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Override path to viewer.html template.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow writing into an output folder that already has manifest.json.",
    )
    p.add_argument(
        "--viewer-only",
        action="store_true",
        help="Rebuild viewer.html + manifests only (needs existing outputs + style_bible.json).",
    )
    p.add_argument(
        "--rebuild-overlays",
        action="store_true",
        help="Recompute UI/holo/gloss + preview from existing PNG layers (no OpenAI).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    except ImportError:
        pass

    args = parse_args(argv)
    root = Path(__file__).resolve().parents[2]

    card: dict
    if args.config:
        card = load_card_config_from_json(args.config)
    else:
        from .config import DEFAULT_CARD_CONFIG

        card = copy.deepcopy(DEFAULT_CARD_CONFIG)

    out = (args.output or (root / "output_card")).resolve()
    tmpl = (args.template or (root / "viewer_template" / "viewer.html")).resolve()

    cfg = default_runtime_config(output_dir=out, viewer_template=tmpl, card_override=card)
    cfg.text_model = TEXT_MODEL
    cfg.image_model = IMAGE_MODEL
    cfg.image_size = IMAGE_SIZE
    cfg.image_quality = IMAGE_QUALITY
    cfg.canvas_size = CANVAS_SIZE

    try:
        if args.viewer_only:
            rebuild_viewer_and_manifests(cfg)
            print(f"Viewer + manifests updated under {out}")
            return 0
        if args.rebuild_overlays:
            rebuild_overlays_preview_manifests(cfg)
            print(f"Overlays + preview + viewer updated under {out}")
            return 0
        manifest = run_full_pipeline(cfg, overwrite=args.overwrite)
        print("Done.")
        print(json.dumps(manifest, indent=2))
        return 0
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run() -> None:
    raise SystemExit(main())
