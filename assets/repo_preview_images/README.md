README hero images live here (`preview_flat.png`, `viewer_parallax.png`, `output_folder.png`).

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
