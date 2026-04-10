README images live here (`preview_flat.png`, `viewer_parallax.png`, `output_folder.png`).

**`hero_showcase.png`** — README hero image (browser / angled desktop shot of the live site). Replace the committed file anytime; the README references it by path.

The primary interactive showcase is still the [live demo](https://iamkuff.github.io/4d-card-generator/) and [`docs/demo/`](../docs/demo/).

Regenerate:

```bash
pip install -r requirements.txt
python scripts/generate_readme_assets.py
```

Replace with real OpenAI pipeline output + layer stack still:

```bash
# OPENAI_API_KEY in env, or put it in .env at repo root
python scripts/generate_readme_assets.py --from-pipeline
```
