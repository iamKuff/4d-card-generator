from __future__ import annotations

from typing import Any, Dict


def with_guardrails(
    prompt: str,
    card_cfg: Dict[str, Any],
    *,
    transparent: bool,
    layer_type: str,
) -> str:
    negative = ", ".join(card_cfg.get("negative_prompt", []))
    base = [
        "premium anime collectible-screen aesthetic",
        "not a real-world physical card photo",
        "no outer card border visible",
        "no watermark",
        "no logo",
        "no baked-in labels or UI text",
        "high detail",
        "strong composition",
    ]
    if transparent:
        base.extend(["transparent background", "clean alpha edges", "isolate the subject cleanly"])
    if layer_type == "player":
        base.extend(["full character visible", "keep limbs complete", "clear silhouette separation"])
    if layer_type.startswith("fx"):
        base.extend(["no human anatomy", "effects only", "transparent negative space around effects"])
    return f"{prompt}. Requirements: {', '.join(base)}. Avoid: {negative}."
