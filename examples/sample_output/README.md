This folder documents the **shape** of a generation run. Actual PNGs are written to `output_card/` (gitignored) when you run the pipeline.

Typical files next to `viewer.html`:

- `character_reference.png` — identity anchor (transparent)
- `background.png` — environment plate
- `player.png` — fitted character (transparent)
- `fx_back.png`, `fx_front.png` — effects (transparent)
- `ui_overlay.png`, `holo_overlay.png`, `gloss_overlay.png` — deterministic overlays
- `preview_composite.png` — **flat** inspection composite only
- `manifest.json`, `scene_manifest.json`, `style_bible.json` — metadata

The browser viewer uses **only** the individual layer PNGs, not `preview_composite.png`.
