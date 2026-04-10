from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def build_manifest(
    project_dir: Path,
    *,
    text_model: str,
    image_model: str,
    viewer_depths: Dict[str, int],
    canvas_size: Tuple[int, int],
) -> Dict[str, Any]:
    recommended_stack: List[str] = [
        "background",
        "holo_overlay",
        "fx_back",
        "player",
        "fx_front",
        "ui_overlay",
        "gloss_overlay",
    ]
    return {
        "project_dir": str(project_dir.resolve()),
        "models": {
            "text_model": text_model,
            "image_model": image_model,
        },
        "layers": {
            "character_reference": "character_reference.png",
            "background": "background.png",
            "player": "player.png",
            "fx_back": "fx_back.png",
            "fx_front": "fx_front.png",
            "ui_overlay": "ui_overlay.png",
            "holo_overlay": "holo_overlay.png",
            "gloss_overlay": "gloss_overlay.png",
            "preview": "preview_composite.png",
            "viewer": "viewer.html",
            "style_bible": "style_bible.json",
        },
        "recommended_stack": recommended_stack,
        "viewer_depths": viewer_depths,
        "notes": [
            "Use individual PNG layers in the viewer, not preview_composite.png.",
            "preview_composite.png is a flat composition for quick inspection only.",
            "The HTML viewer loads each PNG as its own plane with separate Z depth and parallax.",
            "gpt-image-1.5 is used for image generation; gpt-5.4 for planning and the style bible.",
            "Perfect identity lock across separate generations is best-effort; reuse character_reference.png for tighter series work.",
        ],
    }


def write_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_scene_manifest(
    path: Path,
    *,
    stack: List[str],
    depths: Dict[str, int],
    canvas_size: Tuple[int, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "stack": stack,
                "depths": depths,
                "canvas_size": list(canvas_size),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
