from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Models (OpenAI)
TEXT_MODEL = "gpt-5.4"
IMAGE_MODEL = "gpt-image-1.5"
IMAGE_SIZE = "1024x1536"
IMAGE_QUALITY = "high"
CANVAS_SIZE: Tuple[int, int] = (1024, 1536)

DEFAULT_VIEWER_DEPTHS: Dict[str, int] = {
    "background": -18,
    "holo": -8,
    "fx_back": 0,
    "player": 10,
    "fx_front": 16,
    "ui": 22,
    "shine": 26,
}

# Parallax: layer translate multipliers (x, y) relative to normalized pointer -1..1
DEFAULT_PARALLAX_TRANSLATE: Dict[str, Tuple[float, float]] = {
    "background": (-2.0, -2.0),
    "holo": (-1.0, -1.0),
    "fx_back": (1.5, 1.5),
    "player": (3.0, 3.0),
    "fx_front": (4.0, 4.0),
    "ui": (1.0, 1.0),
    "gloss": (0.8, 0.8),
}

DEFAULT_NEGATIVE_PROMPT: List[str] = [
    "physical trading card border",
    "rounded physical card edges",
    "hands cropped badly",
    "extra fingers",
    "watermark",
    "logo",
    "text blocks baked into artwork",
    "low detail",
    "blurry face",
    "duplicate limbs",
    "messy anatomy",
    "cut off head",
    "cut off feet",
    "low contrast face",
    "muddy lighting",
]

DEFAULT_CARD_CONFIG: Dict[str, Any] = {
    "title": "Astra Vey",
    "subtitle": "Prismatic Duelist",
    "theme": "ultra-premium anime player card on a screen, no physical card border",
    "visual_style": (
        "high-end anime illustration, polished collectible-card energy, holographic foil feel, "
        "cinematic lighting, premium game UI, prismatic fantasy-tech vibes"
    ),
    "player_description": (
        "confident anime girl hero, silver-white hair with faint pink and violet gradients, "
        "sharp blue-violet eyes, sleek futuristic combat outfit, elegant rather than overly armored, "
        "heroic pose angled toward camera, stylish and premium"
    ),
    "character_identity": (
        "same girl every time, same face proportions, same hairstyle silhouette, "
        "same armor language, same eye color, same overall age and identity"
    ),
    "background_description": (
        "futuristic neon city skyline with floating crystals, aurora-like light streaks, "
        "cosmic sparkles, premium fantasy-tech atmosphere"
    ),
    "fx_back_description": (
        "subtle energy ribbons, prism haze, soft shards, atmospheric streaks behind the character"
    ),
    "fx_front_description": (
        "hero energy arcs, bright crystalline shards, spark glints, selective foreground flares "
        "in front of the character"
    ),
    "palette": ["violet", "magenta", "cyan", "gold", "white"],
    "stats": {
        "hp": 280,
        "attack_1_name": "Photon Slash",
        "attack_1_cost": 150,
        "attack_2_name": "Nova Spiral",
        "attack_2_cost": 220,
        "weakness": "Void",
        "resistance": "Light",
        "retreat": 2,
    },
    "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
    "viewer_depths": dict(DEFAULT_VIEWER_DEPTHS),
    "viewer": {
        "tilt_max_deg": 10.0,
        "smooth": 0.08,
        "shine_gradient_offset": 20.0,
        "gloss_z_offset": -2,
        "parallax_translate": {k: list(v) for k, v in DEFAULT_PARALLAX_TRANSLATE.items()},
    },
    "fit_player": {
        "target_width_ratio": 0.76,
        "target_height_ratio": 0.70,
        "y_anchor": 0.19,
    },
}


@dataclass
class PathsConfig:
    """Resolved output and template paths."""

    output_dir: Path
    viewer_template: Path


@dataclass
class RuntimeConfig:
    """Merged card + generation settings for one run."""

    card: Dict[str, Any]
    paths: PathsConfig
    text_model: str = TEXT_MODEL
    image_model: str = IMAGE_MODEL
    image_size: str = IMAGE_SIZE
    image_quality: str = IMAGE_QUALITY
    canvas_size: Tuple[int, int] = field(default_factory=lambda: CANVAS_SIZE)


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_card_config_from_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Config must be a JSON object: {path}")
    return deep_merge(DEFAULT_CARD_CONFIG, data)


def default_runtime_config(
    output_dir: Path | None = None,
    viewer_template: Path | None = None,
    card_override: Dict[str, Any] | None = None,
) -> RuntimeConfig:
    root = Path(__file__).resolve().parents[2]
    out = output_dir or (root / "output_card")
    tmpl = viewer_template or (root / "viewer_template" / "viewer.html")
    card = deep_merge(DEFAULT_CARD_CONFIG, card_override or {})
    return RuntimeConfig(
        card=card,
        paths=PathsConfig(output_dir=out.resolve(), viewer_template=tmpl.resolve()),
    )
