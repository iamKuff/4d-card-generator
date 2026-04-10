README images live here (`preview_flat.png`, `viewer_parallax.png`, `output_folder.png`).

**Optional:** add `hero_showcase.png` (browser or angled desktop shot of the live site) for the main README — the primary showcase is now the real card under `docs/demo/` and the [live demo](https://iamkuff.github.io/4d-card-generator/).

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
