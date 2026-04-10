#!/usr/bin/env python3
"""
Backward-compatible entry point.

Prefer: `python generate_card.py` (see README).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.warn(
    "layered_4d_card_pipeline.py is deprecated; use `python generate_card.py` instead.",
    DeprecationWarning,
    stacklevel=2,
)

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fourd_card.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
