from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageFont


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save_rgba(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/Library/Fonts/Arial Bold.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )
    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    )
    for font_path in candidates:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def alpha_bbox(img: Image.Image, threshold: int = 8):
    alpha = img.getchannel("A")
    mask = alpha.point(lambda p: 255 if p > threshold else 0)
    return mask.getbbox()


def autocrop_transparent(img: Image.Image, threshold: int = 8) -> Image.Image:
    bbox = alpha_bbox(img, threshold=threshold)
    if not bbox:
        return img
    return img.crop(bbox)


def fit_layer_inside_card(
    img: Image.Image,
    size: Tuple[int, int],
    *,
    target_width_ratio: float,
    target_height_ratio: float,
    y_anchor: float,
) -> Image.Image:
    w, h = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    img = autocrop_transparent(img)
    iw, ih = img.size
    scale = min((w * target_width_ratio) / iw, (h * target_height_ratio) / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    img = img.resize(new_size, Image.LANCZOS)
    x = (w - img.width) // 2
    y = int(h * y_anchor)
    canvas.alpha_composite(img, (x, y))
    return canvas
