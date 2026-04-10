from __future__ import annotations

import math
from typing import Any, Dict, Tuple

from PIL import Image, ImageDraw, ImageFilter

from .image_helpers import get_font


def make_holo_overlay(size: Tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    px = img.load()

    for y in range(h):
        for x in range(w):
            a = 0.5 + 0.5 * math.sin((x * 0.018) + (y * 0.007))
            b = 0.5 + 0.5 * math.sin((x * 0.004) - (y * 0.021))
            c = 0.5 + 0.5 * math.sin((x * 0.012) + (y * 0.013))
            r = int(90 + 155 * a)
            g = int(80 + 120 * b)
            bl = int(140 + 95 * c)
            al = int(10 + 24 * ((a + b + c) / 3.0))
            px[x, y] = (r, g, bl, al)

    draw = ImageDraw.Draw(img)
    for i in range(-h, w + h, 160):
        draw.line((i, 0, i + h, h), fill=(255, 255, 255, 18), width=4)
        draw.line((i + 16, 0, i + h + 16, h), fill=(255, 220, 255, 10), width=1)

    for i in range(240):
        x = int((i * 97) % w)
        y = int((i * 223) % h)
        r = 1 + (i % 3)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 40))

    return img.filter(ImageFilter.GaussianBlur(0.6))


def _glass_panel(
    draw: ImageDraw.ImageDraw,
    box: Tuple[float, float, float, float],
    radius: float,
    fill: Tuple[int, int, int, int],
    outline: Tuple[int, int, int, int],
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_ui_overlay(size: Tuple[int, int], card_cfg: Dict[str, Any]) -> Image.Image:
    w, h = size
    ui = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui)

    title_font = get_font(62, bold=True)
    sub_font = get_font(30)
    hp_font = get_font(54, bold=True)
    attack_font = get_font(48, bold=True)
    cost_font = get_font(46, bold=True)
    small_font = get_font(24, bold=True)

    stats = card_cfg["stats"]

    _glass_panel(draw, (38, 30, w - 38, 154), 28, (8, 10, 20, 118), (255, 255, 255, 68), 2)
    draw.text((64, 46), str(card_cfg["title"]), font=title_font, fill=(255, 255, 255, 242))
    draw.text((68, 102), str(card_cfg["subtitle"]), font=sub_font, fill=(205, 225, 255, 220))
    draw.text((w - 230, 50), f"HP {stats['hp']}", font=hp_font, fill=(255, 234, 185, 242))

    y1 = int(h * 0.662)
    y2 = y1 + 106
    for y in (y1, y2):
        _glass_panel(draw, (58, y, w - 58, y + 78), 22, (10, 10, 18, 138), (255, 255, 255, 66), 2)

    draw.text((88, y1 + 14), str(stats["attack_1_name"]), font=attack_font, fill=(255, 255, 255, 240))
    draw.text((w - 190, y1 + 14), str(stats["attack_1_cost"]), font=cost_font, fill=(245, 245, 245, 240))

    draw.text((88, y2 + 14), str(stats["attack_2_name"]), font=attack_font, fill=(255, 255, 255, 240))
    draw.text((w - 190, y2 + 14), str(stats["attack_2_cost"]), font=cost_font, fill=(255, 240, 205, 240))

    strip_y = h - 110
    _glass_panel(draw, (40, strip_y, w - 40, h - 30), 22, (10, 10, 16, 128), (255, 255, 255, 62), 2)
    draw.text((76, strip_y + 26), f"WEAKNESS  {stats['weakness']}", font=small_font, fill=(255, 255, 255, 225))
    draw.text((352, strip_y + 26), f"RESIST  {stats['resistance']}", font=small_font, fill=(255, 255, 255, 225))
    draw.text((704, strip_y + 26), f"RETREAT  {stats['retreat']}", font=small_font, fill=(255, 255, 255, 225))

    gloss = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.rounded_rectangle((54, 40, w - 54, 82), radius=18, fill=(255, 255, 255, 20))
    gd.rounded_rectangle((68, y1 + 8, w - 68, y1 + 28), radius=18, fill=(255, 255, 255, 16))
    gd.rounded_rectangle((68, y2 + 8, w - 68, y2 + 28), radius=18, fill=(255, 255, 255, 16))
    gd.rounded_rectangle((52, strip_y + 6, w - 52, strip_y + 24), radius=16, fill=(255, 255, 255, 12))
    gloss = gloss.filter(ImageFilter.GaussianBlur(2.5))

    edge = Image.new("RGBA", size, (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rounded_rectangle((30, 24, w - 30, h - 24), radius=30, outline=(255, 255, 255, 18), width=2)
    edge = edge.filter(ImageFilter.GaussianBlur(1.0))

    return Image.alpha_composite(Image.alpha_composite(ui, gloss), edge)


def make_gloss_overlay(size: Tuple[int, int]) -> Image.Image:
    w, h = size
    gloss = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(gloss)
    d.polygon([(0, 0), (int(w * 0.62), 0), (int(w * 0.34), h), (0, h)], fill=(255, 255, 255, 18))
    d.polygon([(int(w * 0.72), 0), (w, 0), (w, h), (int(w * 0.86), h)], fill=(255, 255, 255, 8))
    return gloss.filter(ImageFilter.GaussianBlur(18))


def compose_preview(
    bg: Image.Image,
    holo: Image.Image,
    fx_back: Image.Image,
    player: Image.Image,
    fx_front: Image.Image,
    ui: Image.Image,
    gloss: Image.Image,
) -> Image.Image:
    out = bg.copy().convert("RGBA")
    for layer in (holo, fx_back, player, fx_front, ui, gloss):
        out = Image.alpha_composite(out, layer)
    return out
