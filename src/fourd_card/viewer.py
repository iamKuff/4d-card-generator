from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def build_scene_config(card_cfg: Dict[str, Any]) -> Dict[str, Any]:
    depths = dict(card_cfg.get("viewer_depths") or {})
    viewer = card_cfg.get("viewer") or {}
    gloss_z = int(viewer.get("gloss_z_offset", -2))
    return {
        "depths": depths,
        "viewer": {
            "tilt_max_deg": float(viewer.get("tilt_max_deg", 10.0)),
            "smooth": float(viewer.get("smooth", 0.08)),
            "shine_gradient_offset": float(viewer.get("shine_gradient_offset", 20.0)),
            "gloss_z_offset": gloss_z,
        },
        "parallax_translate": viewer.get("parallax_translate")
        or {
            "background": [-2, -2],
            "holo": [-1, -1],
            "fx_back": [1.5, 1.5],
            "player": [3, 3],
            "fx_front": [4, 4],
            "ui": [1, 1],
            "gloss": [0.8, 0.8],
        },
    }


def render_viewer_html(template_path: Path, scene: Dict[str, Any]) -> str:
    if not template_path.is_file():
        raise FileNotFoundError(f"Viewer template not found: {template_path}")
    raw = template_path.read_text(encoding="utf-8")
    payload = json.dumps(scene, separators=(",", ":")).replace("<", "\\u003c")
    if "__FOURD_SCENE__" not in raw:
        raise ValueError("viewer.html template must contain __FOURD_SCENE__ placeholder")
    return raw.replace("__FOURD_SCENE__", payload)


def write_viewer_html(project_dir: Path, template_path: Path, card_cfg: Dict[str, Any]) -> None:
    scene = build_scene_config(card_cfg)
    html = render_viewer_html(template_path, scene)
    out = project_dir / "viewer.html"
    project_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
