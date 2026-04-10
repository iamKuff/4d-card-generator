from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class StyleBible:
    title: str
    character_anchor: str
    wardrobe_anchor: str
    face_anchor: str
    pose_anchor: str
    camera_anchor: str
    palette_anchor: str
    lighting_anchor: str
    texture_anchor: str
    environment_anchor: str
    composition_anchor: str
    forbidden_elements: List[str]
    master_prompt: str
    character_reference_prompt: str
    background_prompt: str
    player_prompt: str
    fx_back_prompt: str
    fx_front_prompt: str

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict

        return asdict(self)
