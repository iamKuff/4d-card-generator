from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict

from openai import OpenAI

from .config import TEXT_MODEL
from .models import StyleBible


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env or export the variable, then retry."
        )
    return OpenAI(api_key=api_key)


def save_b64_png(b64_data: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(b64_data))


def extract_first_image_b64(image_response: Any) -> str:
    if not getattr(image_response, "data", None):
        raise RuntimeError("No image data returned by the Images API.")
    item = image_response.data[0]
    b64_data = getattr(item, "b64_json", None)
    if not b64_data:
        raise RuntimeError("Expected b64_json in image response but none was returned.")
    return b64_data


def build_style_bible(
    client: OpenAI,
    card_cfg: Dict[str, Any],
    *,
    text_model: str,
    output_path: Path,
) -> StyleBible:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "character_anchor": {"type": "string"},
            "wardrobe_anchor": {"type": "string"},
            "face_anchor": {"type": "string"},
            "pose_anchor": {"type": "string"},
            "camera_anchor": {"type": "string"},
            "palette_anchor": {"type": "string"},
            "lighting_anchor": {"type": "string"},
            "texture_anchor": {"type": "string"},
            "environment_anchor": {"type": "string"},
            "composition_anchor": {"type": "string"},
            "forbidden_elements": {"type": "array", "items": {"type": "string"}},
            "master_prompt": {"type": "string"},
            "character_reference_prompt": {"type": "string"},
            "background_prompt": {"type": "string"},
            "player_prompt": {"type": "string"},
            "fx_back_prompt": {"type": "string"},
            "fx_front_prompt": {"type": "string"},
        },
        "required": [
            "title",
            "character_anchor",
            "wardrobe_anchor",
            "face_anchor",
            "pose_anchor",
            "camera_anchor",
            "palette_anchor",
            "lighting_anchor",
            "texture_anchor",
            "environment_anchor",
            "composition_anchor",
            "forbidden_elements",
            "master_prompt",
            "character_reference_prompt",
            "background_prompt",
            "player_prompt",
            "fx_back_prompt",
            "fx_front_prompt",
        ],
    }

    prompt = f"""
Create a production-ready style bible for a deluxe layered 4D online player card.
Return strict JSON matching the schema.

Project goals:
- This is NOT a Pokemon card.
- It should feel like a premium anime collectible card shown on a screen.
- No physical card border edges.
- Assets must be consistent across separate generations.
- We need these layers:
  1) character_reference only, clean character identity anchor, transparent background
  2) background only
  3) player only with transparent background
  4) fx_back overlay, transparent background
  5) fx_front overlay, transparent background
  6) local UI overlay added later by code

Important:
- The same exact character identity must survive across all prompts.
- Background must not include the player.
- Player prompt must not include UI text.
- FX prompts must not include character anatomy.
- Use strong consistency anchors but keep prompts concise.
- Design the prompts for premium collectible-card depth and holographic energy.

User config:
{json.dumps(card_cfg, indent=2)}
""".strip()

    response = client.responses.create(
        model=text_model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "style_bible",
                "schema": schema,
                "strict": True,
            }
        },
    )

    data = json.loads(response.output_text)
    bible = StyleBible(**data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bible.to_dict(), indent=2), encoding="utf-8")
    return bible


def generate_image(
    client: OpenAI,
    prompt: str,
    output_path: Path,
    *,
    image_model: str,
    transparent: bool = False,
    size: str,
    quality: str,
) -> None:
    response = client.images.generate(
        model=image_model,
        prompt=prompt,
        size=size,
        quality=quality,
        output_format="png",
        background="transparent" if transparent else "opaque",
    )
    save_b64_png(extract_first_image_b64(response), output_path)
