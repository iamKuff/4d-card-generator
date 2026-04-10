from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from PIL import Image

from .config import RuntimeConfig
from .image_helpers import fit_layer_inside_card, load_rgba, save_rgba
from .manifests import build_manifest, write_manifest, write_scene_manifest
from .openai_pipeline import build_style_bible, generate_image, get_client
from .overlays import compose_preview, make_gloss_overlay, make_holo_overlay, make_ui_overlay
from .prompts import with_guardrails
from .viewer import write_viewer_html


def _require_file(path: Path, what: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{what} not found: {path}")


def rebuild_viewer_and_manifests(cfg: RuntimeConfig) -> None:
    """Regenerate viewer.html and JSON manifests from existing output folder."""
    out = cfg.paths.output_dir
    _require_file(out / "style_bible.json", "style_bible.json")
    manifest = build_manifest(
        out,
        text_model=cfg.text_model,
        image_model=cfg.image_model,
        viewer_depths=cfg.card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_manifest(out / "manifest.json", manifest)
    write_scene_manifest(
        out / "scene_manifest.json",
        stack=manifest["recommended_stack"],
        depths=cfg.card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_viewer_html(out, cfg.paths.viewer_template, cfg.card)


def rebuild_overlays_preview_manifests(cfg: RuntimeConfig) -> None:
    """Recompute deterministic overlays + flat preview + manifests + viewer (no OpenAI)."""
    out = cfg.paths.output_dir
    w, h = cfg.canvas_size
    for name in ("background.png", "fx_back.png", "fx_front.png", "player.png"):
        _require_file(out / name, name)

    bg = load_rgba(out / "background.png").resize(cfg.canvas_size, resample=Image.LANCZOS)
    fx_back = load_rgba(out / "fx_back.png").resize(cfg.canvas_size, resample=Image.LANCZOS)
    fx_front = load_rgba(out / "fx_front.png").resize(cfg.canvas_size, resample=Image.LANCZOS)
    player = load_rgba(out / "player.png")

    ui = make_ui_overlay(cfg.canvas_size, cfg.card)
    holo = make_holo_overlay(cfg.canvas_size)
    gloss = make_gloss_overlay(cfg.canvas_size)

    save_rgba(ui, out / "ui_overlay.png")
    save_rgba(holo, out / "holo_overlay.png")
    save_rgba(gloss, out / "gloss_overlay.png")

    preview = compose_preview(bg, holo, fx_back, player, fx_front, ui, gloss)
    save_rgba(preview, out / "preview_composite.png")

    manifest = build_manifest(
        out,
        text_model=cfg.text_model,
        image_model=cfg.image_model,
        viewer_depths=cfg.card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_manifest(out / "manifest.json", manifest)
    write_scene_manifest(
        out / "scene_manifest.json",
        stack=manifest["recommended_stack"],
        depths=cfg.card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_viewer_html(out, cfg.paths.viewer_template, cfg.card)


def run_full_pipeline(cfg: RuntimeConfig, *, overwrite: bool) -> Dict[str, Any]:
    out = cfg.paths.output_dir
    out.mkdir(parents=True, exist_ok=True)

    def out_path(name: str) -> Path:
        return out / name

    if not overwrite:
        marker = out_path("manifest.json")
        if marker.exists():
            raise RuntimeError(
                f"Output already exists at {out}. Pass --overwrite or choose a different --output."
            )

    client = get_client()
    card = cfg.card

    print("[1/8] Building style bible...")
    bible = build_style_bible(
        client,
        card,
        text_model=cfg.text_model,
        output_path=out_path("style_bible.json"),
    )

    print("[2/8] Generating character reference...")
    generate_image(
        client,
        with_guardrails(
            bible.character_reference_prompt, card, transparent=True, layer_type="player"
        ),
        out_path("character_reference.png"),
        image_model=cfg.image_model,
        transparent=True,
        size=cfg.image_size,
        quality=cfg.image_quality,
    )

    print("[3/8] Generating background...")
    generate_image(
        client,
        with_guardrails(bible.background_prompt, card, transparent=False, layer_type="background"),
        out_path("background.png"),
        image_model=cfg.image_model,
        transparent=False,
        size=cfg.image_size,
        quality=cfg.image_quality,
    )

    print("[4/8] Generating player...")
    generate_image(
        client,
        with_guardrails(bible.player_prompt, card, transparent=True, layer_type="player"),
        out_path("player_raw.png"),
        image_model=cfg.image_model,
        transparent=True,
        size=cfg.image_size,
        quality=cfg.image_quality,
    )

    print("[5/8] Generating FX back...")
    generate_image(
        client,
        with_guardrails(bible.fx_back_prompt, card, transparent=True, layer_type="fx_back"),
        out_path("fx_back.png"),
        image_model=cfg.image_model,
        transparent=True,
        size=cfg.image_size,
        quality=cfg.image_quality,
    )

    print("[6/8] Generating FX front...")
    generate_image(
        client,
        with_guardrails(bible.fx_front_prompt, card, transparent=True, layer_type="fx_front"),
        out_path("fx_front.png"),
        image_model=cfg.image_model,
        transparent=True,
        size=cfg.image_size,
        quality=cfg.image_quality,
    )

    print("[7/8] Fitting player + rendering local overlays...")
    player_raw = load_rgba(out_path("player_raw.png"))
    fit = card.get("fit_player") or {}
    player = fit_layer_inside_card(
        player_raw,
        cfg.canvas_size,
        target_width_ratio=float(fit.get("target_width_ratio", 0.76)),
        target_height_ratio=float(fit.get("target_height_ratio", 0.70)),
        y_anchor=float(fit.get("y_anchor", 0.19)),
    )
    save_rgba(player, out_path("player.png"))

    bg = load_rgba(out_path("background.png")).resize(cfg.canvas_size, resample=Image.LANCZOS)
    fx_back = load_rgba(out_path("fx_back.png")).resize(cfg.canvas_size, resample=Image.LANCZOS)
    fx_front = load_rgba(out_path("fx_front.png")).resize(cfg.canvas_size, resample=Image.LANCZOS)

    ui = make_ui_overlay(cfg.canvas_size, card)
    holo = make_holo_overlay(cfg.canvas_size)
    gloss = make_gloss_overlay(cfg.canvas_size)

    save_rgba(ui, out_path("ui_overlay.png"))
    save_rgba(holo, out_path("holo_overlay.png"))
    save_rgba(gloss, out_path("gloss_overlay.png"))

    print("[8/8] Preview + viewer + manifests...")
    preview = compose_preview(bg, holo, fx_back, player, fx_front, ui, gloss)
    save_rgba(preview, out_path("preview_composite.png"))

    manifest = build_manifest(
        out,
        text_model=cfg.text_model,
        image_model=cfg.image_model,
        viewer_depths=card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_manifest(out_path("manifest.json"), manifest)
    write_scene_manifest(
        out_path("scene_manifest.json"),
        stack=manifest["recommended_stack"],
        depths=card["viewer_depths"],
        canvas_size=cfg.canvas_size,
    )
    write_viewer_html(out, cfg.paths.viewer_template, card)

    return manifest
