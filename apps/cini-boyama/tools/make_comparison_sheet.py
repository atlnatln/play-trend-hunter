#!/usr/bin/env python3
"""
Eski ve yeni line-art'ları yan yana karşılaştıran bir kolaj üretir.
Çıktı: tools/lineart_comparison.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OLD_DIR = ROOT / "app/src/main/res/drawable-nodpi/backup_before_fix"
NEW_DIR = ROOT / "app/src/main/res/drawable-nodpi"
OUT_PATH = ROOT / "tools" / "lineart_comparison.png"

NAMES = [
    "lineart_iznik_tile",
    "lineart_iznik_vase",
    "lineart_flower",
    "lineart_geometric",
    "lineart_car_tile",
    "lineart_dino_mandala",
    "lineart_rocket_stars",
    "lineart_soccer_mandala",
    "lineart_butterfly_tile",
    "lineart_unicorn_mandala",
    "lineart_princess_crown",
    "lineart_heart_mandala",
]

THUMB_SIZE = 256
MARGIN = 20
TEXT_H = 24


def load_thumb(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    img = Image.open(path).convert("L")
    return img.resize((THUMB_SIZE, THUMB_SIZE), Image.Resampling.LANCZOS)


def main() -> None:
    rows = []
    for name in NAMES:
        old = load_thumb(OLD_DIR / f"{name}.png")
        new = load_thumb(NEW_DIR / f"{name}.png")
        if old and new:
            rows.append((name, old, new))

    if not rows:
        print("Karşılaştırılacak görsel bulunamadı. Önce yedekleme yapılmalı.")
        return

    font = ImageFont.load_default()
    w = THUMB_SIZE * 2 + MARGIN * 3
    h = (THUMB_SIZE + TEXT_H + MARGIN) * len(rows) + MARGIN

    canvas = Image.new("RGB", (w, h), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)

    # Başlıklar
    draw.text((MARGIN + THUMB_SIZE // 2 - 30, 4), "ESKİ", fill=(80, 80, 80), font=font)
    draw.text((MARGIN * 2 + THUMB_SIZE + THUMB_SIZE // 2 - 30, 4), "YENİ", fill=(80, 80, 80), font=font)

    y = MARGIN + TEXT_H
    for name, old, new in rows:
        # Etiket
        draw.text((MARGIN, y - TEXT_H + 4), name, fill=(40, 40, 40), font=font)
        # Görüntüler
        canvas.paste(old.convert("RGB"), (MARGIN, y))
        canvas.paste(new.convert("RGB"), (MARGIN * 2 + THUMB_SIZE, y))
        y += THUMB_SIZE + MARGIN + TEXT_H

    canvas.save(OUT_PATH)
    print(f"Karşılaştırma kaydedildi: {OUT_PATH}")


if __name__ == "__main__":
    main()
