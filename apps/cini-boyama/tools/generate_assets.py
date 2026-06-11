#!/usr/bin/env python3
"""
Çini Boyama varlık üretim aracı.

- Mevcut 512x512 desenleri 1024x1024'e upscale eder ve hatları hafif kalınlaştırarak
  boyama bölgelerini telefon ekranlarına daha uygun hale getirir.
- Çocukların ilgisini çekecek figürleri (erkek ve kız temaları ayrı ayrı)
  geleneksel İznik çini sanatıyla birleştirir.
- Her desen için hem renkli preview hem siyah-beyaz line-art üretir.

Gereksinimler:
    source /home/akn/local/uygulama-gelistir-play/.venv/bin/activate
    # veya: python3 -m pip install Pillow numpy scipy opencv-python-headless

Kullanım:
    cd apps/cini-boyama
    python3 tools/generate_assets.py
"""

from __future__ import annotations

import math
from pathlib import Path


import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

# -----------------------------------------------------------------------------
# Yapılandırma
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "app/src/main/res/drawable-nodpi"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = 1024
PREVIEW_SIZE = 512

# İznik paleti
C = {
    "kobalt": (30, 58, 138),
    "turkuaz": (14, 165, 233),
    "yesil": (4, 120, 87),
    "kirmizi": (185, 28, 28),
    "sari": (245, 158, 11),
    "krem": (254, 243, 199),
    "beyaz": (255, 255, 255),
    "siyah": (17, 24, 39),
    "mor": (124, 58, 237),
    "pembe": (236, 72, 153),
    "kahve": (146, 64, 14),
    "altin": (212, 175, 55),
}
IZNIK_COLORS = list(C.values())

# -----------------------------------------------------------------------------
# Yardımcılar
# -----------------------------------------------------------------------------

def new_rgb(fill=(255, 255, 255)) -> Image.Image:
    return Image.new("RGB", (SIZE, SIZE), fill)


def new_lineart() -> Image.Image:
    return Image.new("L", (SIZE, SIZE), 255)


def to_gray(img: Image.Image) -> Image.Image:
    return img.convert("L")


def preview_to_lineart(
    img: Image.Image,
    canny_low: int = 50,
    canny_high: int = 150,
    dilation_size: int = 3,
    dilation_iterations: int = 2,
    min_component_size: int = 30,
    blur_kernel: int = 5,
    clahe_clip: float = 2.0,
    use_legacy_edges: bool = False,
) -> Image.Image:
    """
    Renkli preview görselinden line-art üretir.

    Varsayılan olarak OpenCV Canny + dilation kullanır. Çok küçük detaylı
    desenler (örn. geometric karo) için use_legacy_edges=True seçeneğiyle
    PIL FIND_EDGES + scipy grey_dilation yöntemi de kullanılabilir.

    Akış (Canny modu):
      1. Gaussian blur ile yumuşatma (gürültü azaltma)
      2. CLAHE ile kontrast artırma
      3. Canny edge detection
      4. Dilation ile hatları kalınlaştırma
      5. Connected-component analizi ile küçük gürültüleri temizleme
      6. Beyaz arka plan üzerine siyah hatlar
    """
    if use_legacy_edges:
        gray = img.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        arr = np.array(edges)
        dilated = ndimage.grey_dilation(arr, size=(dilation_size, dilation_size))
        binary = dilated > canny_low  # eski 'threshold' yerine canny_low kullan
        labeled, num = ndimage.label(binary)
        sizes = ndimage.sum(binary, labeled, range(1, num + 1))
        mask = np.concatenate(([False], sizes >= min_component_size))
        binary = mask[labeled]
        out = (np.where(binary, 0, 255)).astype(np.uint8)
        return Image.fromarray(out, "L")

    gray = np.array(img.convert("L"))

    # 1. Yumuşatma
    if blur_kernel > 1:
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
    else:
        blurred = gray

    # 2. Kontrast artırma
    if clahe_clip > 0:
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
    else:
        enhanced = blurred

    # 3. Canny kenar tespiti
    edges = cv2.Canny(enhanced, canny_low, canny_high)

    # 4. Hat kalınlaştırma
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_size, dilation_size))
    thick = cv2.dilate(edges, kernel, iterations=dilation_iterations)

    # 5. Küçük gürültüleri temizle
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thick, connectivity=8)
    cleaned = np.zeros_like(thick)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_component_size:
            cleaned[labels == i] = 255

    # 6. Beyaz arka plan, siyah hat
    out = 255 - cleaned
    return Image.fromarray(out, "L")


def upscale_preview(src: Path, dest: Path) -> None:
    Image.open(src).convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(dest)


# -----------------------------------------------------------------------------
# Çini deseni elemanları
# -----------------------------------------------------------------------------

def draw_iznik_border(draw: ImageDraw.ImageDraw, margin: int, color, width: int = 6):
    s = margin
    e = SIZE - margin
    draw.rectangle([s, s, e, e], outline=color, width=width)
    draw.rectangle([s + 16, s + 16, e - 16, e - 16], outline=color, width=max(2, width - 2))


def draw_corner_flowers(draw: ImageDraw.ImageDraw, margin: int, color, radius: int = 28):
    offset = margin + 36
    for x, y in [(offset, offset), (SIZE - offset, offset), (offset, SIZE - offset), (SIZE - offset, SIZE - offset)]:
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=color, outline=C["siyah"])
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = x + int(radius * math.cos(rad))
            py = y + int(radius * math.sin(rad))
            draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=color, outline=C["siyah"])


def draw_radial_petals(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, petals: int, color, width: int = 4):
    for i in range(petals):
        angle = (2 * math.pi * i) / petals
        x1 = cx + int(radius * 0.35 * math.cos(angle))
        y1 = cy + int(radius * 0.35 * math.sin(angle))
        x2 = cx + int(radius * math.cos(angle))
        y2 = cy + int(radius * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
        ux, uy = x2, y2
        for sub in (-0.28, 0.28):
            a2 = angle + sub
            vx = ux + int(radius * 0.18 * math.cos(a2))
            vy = uy + int(radius * 0.18 * math.sin(a2))
            draw.line([(ux, uy), (vx, vy)], fill=color, width=width)


def draw_rosette(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color, width: int = 4):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=width)
    draw.ellipse([cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2], outline=color, width=max(2, width - 1))
    for i in range(8):
        angle = (2 * math.pi * i) / 8
        x1 = cx + int((radius // 2) * math.cos(angle))
        y1 = cy + int((radius // 2) * math.sin(angle))
        x2 = cx + int(radius * math.cos(angle))
        y2 = cy + int(radius * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


def draw_tile_background(draw: ImageDraw.ImageDraw, tile_size: int = 128, palette=None):
    palette = palette or [C["kobalt"], C["turkuaz"], C["yesil"], C["kirmizi"], C["sari"], C["mor"]]
    for y in range(0, SIZE, tile_size):
        for x in range(0, SIZE, tile_size):
            col = palette[(x // tile_size + y // tile_size) % len(palette)]
            light = tuple(min(255, v + 110) for v in col)
            draw.rectangle([x, y, x + tile_size, y + tile_size], fill=light, outline=col, width=3)
            draw_rosette(draw, x + tile_size // 2, y + tile_size // 2, 30, col, width=2)


# -----------------------------------------------------------------------------
# Erkek temalı figürler
# -----------------------------------------------------------------------------

def draw_racing_car(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    body_color = C["kirmizi"]
    window_color = C["turkuaz"]
    # Araba gövdesi (alçak spor araba)
    body_top = cy - int(30 * s)
    body_bottom = cy + int(40 * s)
    left = cx - int(140 * s)
    right = cx + int(140 * s)
    draw.rounded_rectangle([left, body_top, right, body_bottom], radius=int(30 * s), fill=body_color, outline=C["siyah"], width=4)
    # Üst kabin
    cabin_left = cx - int(80 * s)
    cabin_right = cx + int(70 * s)
    cabin_top = cy - int(80 * s)
    draw.polygon([(cabin_left, body_top), (cx - int(50 * s), cabin_top), (cx + int(50 * s), cabin_top), (cabin_right, body_top)],
                 fill=window_color, outline=C["siyah"])
    # Tekerlekler
    wheel_r = int(28 * s)
    for wx in [cx - int(75 * s), cx + int(75 * s)]:
        draw.ellipse([wx - wheel_r, body_bottom - wheel_r - int(5 * s), wx + wheel_r, body_bottom + wheel_r - int(5 * s)],
                     fill=C["siyah"], outline=C["siyah"], width=3)
        draw.ellipse([wx - int(10 * s), body_bottom - int(15 * s), wx + int(10 * s), body_bottom + int(5 * s)], fill=C["beyaz"])
    # Farlar
    draw.ellipse([right - int(25 * s), body_top + int(10 * s), right - int(5 * s), body_top + int(30 * s)], fill=C["sari"], outline=C["siyah"])


def draw_dinosaur(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    color = C["yesil"]
    # Vücut (oval yatay)
    body_w, body_h = int(130 * s), int(90 * s)
    body_left = cx - body_w
    body_right = cx + body_w
    body_top = cy - body_h // 2
    body_bottom = cy + body_h // 2
    draw.ellipse([body_left, body_top, body_right, body_bottom], fill=color, outline=C["siyah"], width=4)
    # Boyun + kafa
    neck_x = body_left + int(40 * s)
    neck_top = cy - int(120 * s)
    draw.rounded_rectangle([neck_x - int(25 * s), neck_top, neck_x + int(25 * s), body_top], radius=int(12 * s),
                           fill=color, outline=C["siyah"], width=4)
    head_r = int(45 * s)
    draw.ellipse([neck_x - head_r, neck_top - head_r, neck_x + head_r, neck_top + head_r],
                 fill=color, outline=C["siyah"], width=4)
    # Göz
    draw.ellipse([neck_x + int(15 * s), neck_top - int(15 * s), neck_x + int(30 * s), neck_top], fill=C["siyah"])
    # Ağız
    draw.arc([neck_x - int(20 * s), neck_top - int(10 * s), neck_x + int(20 * s), neck_top + int(30 * s)],
             start=200, end=340, fill=C["siyah"], width=3)
    # Kuyruk
    tail_points = [
        (body_right, cy),
        (body_right + int(80 * s), cy - int(40 * s)),
        (body_right + int(100 * s), cy + int(20 * s)),
        (body_right, cy + int(30 * s)),
    ]
    draw.polygon(tail_points, fill=color, outline=C["siyah"])
    # Bacaklar
    for lx in [body_left + int(50 * s), body_right - int(50 * s)]:
        draw.rounded_rectangle([lx - int(18 * s), body_bottom, lx + int(18 * s), body_bottom + int(60 * s)],
                               radius=int(9 * s), fill=color, outline=C["siyah"], width=3)
    # Sırtındaki dikenler
    for i in range(5):
        sx = body_left + int(40 * s) + i * int(45 * s)
        sy = body_top
        draw.polygon([(sx, sy), (sx + int(15 * s), sy - int(25 * s)), (sx + int(30 * s), sy)], fill=C["sari"], outline=C["siyah"])


def draw_rocket(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    body_color = C["beyaz"]
    fin_color = C["kirmizi"]
    # Roket gövdesi
    body_w = int(50 * s)
    body_h = int(160 * s)
    top = cy - body_h
    draw.polygon([
        (cx, top - int(50 * s)),
        (cx + body_w, top),
        (cx + body_w, cy + body_h),
        (cx - body_w, cy + body_h),
        (cx - body_w, top),
    ], fill=body_color, outline=C["siyah"], width=4)
    # Pencere
    win_r = int(30 * s)
    draw.ellipse([cx - win_r, top + int(40 * s), cx + win_r, top + int(100 * s)], fill=C["turkuaz"], outline=C["siyah"], width=3)
    # Kanatlar
    draw.polygon([
        (cx - body_w, cy + int(60 * s)),
        (cx - body_w - int(50 * s), cy + body_h + int(10 * s)),
        (cx - body_w, cy + body_h),
    ], fill=fin_color, outline=C["siyah"], width=3)
    draw.polygon([
        (cx + body_w, cy + int(60 * s)),
        (cx + body_w + int(50 * s), cy + body_h + int(10 * s)),
        (cx + body_w, cy + body_h),
    ], fill=fin_color, outline=C["siyah"], width=3)
    # Alev
    draw.polygon([
        (cx - int(25 * s), cy + body_h),
        (cx, cy + body_h + int(70 * s)),
        (cx + int(25 * s), cy + body_h),
    ], fill=C["sari"], outline=C["siyah"], width=3)


def draw_soccer_ball(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=C["beyaz"], outline=C["siyah"], width=4)
    # Üçgenlerden oluşan klasik futbol topu deseni
    r = radius
    hex_r = int(r * 0.35)
    # Merkez altıgen
    hex_points = []
    for i in range(6):
        angle = math.radians(i * 60)
        hex_points.append((cx + int(hex_r * math.cos(angle)), cy + int(hex_r * math.sin(angle))))
    draw.polygon(hex_points, fill=C["siyah"], outline=C["siyah"])
    # Çevresindeki bağlantı çizgileri
    for i in range(6):
        angle = math.radians(i * 60)
        x = cx + int(r * 0.9 * math.cos(angle))
        y = cy + int(r * 0.9 * math.sin(angle))
        draw.line([(cx + int(hex_r * math.cos(angle)), cy + int(hex_r * math.sin(angle))), (x, y)], fill=C["siyah"], width=3)
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=C["beyaz"], outline=C["siyah"], width=2)


# -----------------------------------------------------------------------------
# Kız temalı figürler
# -----------------------------------------------------------------------------

def draw_butterfly(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    wing_color = C["pembe"]
    # Gövde
    body_w = int(12 * s)
    body_h = int(90 * s)
    draw.ellipse([cx - body_w, cy - body_h, cx + body_w, cy + body_h], fill=C["siyah"], outline=C["siyah"], width=3)
    # Antenler
    draw.line([(cx, cy - body_h), (cx - int(25 * s), cy - body_h - int(40 * s))], fill=C["siyah"], width=3)
    draw.line([(cx, cy - body_h), (cx + int(25 * s), cy - body_h - int(40 * s))], fill=C["siyah"], width=3)
    # Üst kanatlar (büyük)
    top_wing_w, top_wing_h = int(80 * s), int(90 * s)
    for sign in (-1, 1):
        wx = cx + sign * (body_w + top_wing_w // 2)
        wy = cy - body_h // 2
        draw.ellipse([wx - top_wing_w, wy - top_wing_h, wx + top_wing_w, wy + top_wing_h],
                     fill=wing_color, outline=C["siyah"], width=3)
        # Desen (sol/sağ için koordinatları doğru sırala)
        dx1, dx2 = int(10 * s), int(30 * s)
        if sign < 0:
            # sol kanat: wx + 10 ile wx + 30
            draw.ellipse([wx + dx1, wy - int(20 * s), wx + dx2, wy + int(10 * s)],
                         fill=C["sari"], outline=C["siyah"], width=2)
        else:
            # sağ kanat: wx - 30 ile wx - 10
            draw.ellipse([wx - dx2, wy - int(20 * s), wx - dx1, wy + int(10 * s)],
                         fill=C["sari"], outline=C["siyah"], width=2)
    # Alt kanatlar (küçük)
    bot_wing_w, bot_wing_h = int(50 * s), int(60 * s)
    for sign in (-1, 1):
        wx = cx + sign * (body_w + bot_wing_w // 2)
        wy = cy + body_h // 2
        draw.ellipse([wx - bot_wing_w, wy - bot_wing_h, wx + bot_wing_w, wy + bot_wing_h],
                     fill=wing_color, outline=C["siyah"], width=3)


def draw_unicorn(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    body_color = C["beyaz"]
    mane_color = C["pembe"]
    horn_color = C["sari"]
    # Gövde
    draw.ellipse([cx - int(80 * s), cy - int(40 * s), cx + int(80 * s), cy + int(60 * s)],
                 fill=body_color, outline=C["siyah"], width=4)
    # Bacaklar
    for lx in [cx - int(45 * s), cx + int(45 * s)]:
        draw.rounded_rectangle([lx - int(15 * s), cy + int(40 * s), lx + int(15 * s), cy + int(110 * s)],
                               radius=int(8 * s), fill=body_color, outline=C["siyah"], width=3)
    # Kafa
    head_r = int(45 * s)
    hx, hy = cx + int(70 * s), cy - int(50 * s)
    draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=body_color, outline=C["siyah"], width=4)
    # Boynuz
    draw.polygon([(hx + int(10 * s), hy - head_r), (hx + int(25 * s), hy - head_r - int(60 * s)), (hx + int(35 * s), hy - head_r)],
                 fill=horn_color, outline=C["siyah"], width=3)
    # Yele (yelesi)
    for i in range(4):
        px = hx - int(30 * s) - i * int(20 * s)
        py = hy + int(10 * s) + i * int(15 * s)
        draw.ellipse([px - int(15 * s), py - int(25 * s), px + int(5 * s), py + int(5 * s)], fill=mane_color, outline=C["siyah"], width=2)
    # Göz
    draw.ellipse([hx + int(10 * s), hy - int(10 * s), hx + int(22 * s), hy + int(5 * s)], fill=C["siyah"])
    # Kuyruk
    draw.polygon([(cx - int(70 * s), cy - int(10 * s)), (cx - int(130 * s), cy - int(50 * s)), (cx - int(120 * s), cy + int(20 * s))],
                 fill=mane_color, outline=C["siyah"], width=3)


def draw_crown(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    s = scale
    color = C["sari"]
    w = int(140 * s)
    h = int(70 * s)
    base_y = cy + h // 2
    # Taban
    draw.arc([cx - w, cy - h, cx + w, base_y], start=0, end=180, fill=C["siyah"], width=4)
    draw.pieslice([cx - w, cy - h, cx + w, base_y], start=0, end=180, fill=color, outline=C["siyah"])
    # Dişler
    teeth = 5
    for i in range(teeth):
        tx = cx - w + (2 * w * i) // (teeth - 1)
        top_y = cy - h - int(30 * s) if i % 2 == 0 else cy - h - int(15 * s)
        draw.polygon([(tx - int(10 * s), cy - h), (tx, top_y), (tx + int(10 * s), cy - h)], fill=color, outline=C["siyah"], width=2)
    # Jewels
    for i in range(teeth):
        tx = cx - w + (2 * w * i) // (teeth - 1)
        jewel_color = C["kirmizi"] if i == 2 else C["pembe"]
        draw.ellipse([tx - int(8 * s), cy - h + int(10 * s), tx + int(8 * s), cy - h + int(30 * s)], fill=jewel_color, outline=C["siyah"], width=2)


def draw_heart_mandala_center(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color):
    # Kalp şekli
    r = radius
    top_y = cy - r // 3
    # Sol üst yuvarlak
    draw.ellipse([cx - r, top_y - r, cx, top_y + r], fill=color, outline=C["siyah"], width=3)
    # Sağ üst yuvarlak
    draw.ellipse([cx, top_y - r, cx + r, top_y + r], fill=color, outline=C["siyah"], width=3)
    # Alt kısım üçgen
    draw.polygon([(cx - r, top_y + r // 2), (cx + r, top_y + r // 2), (cx, cy + r + r // 3)],
                 fill=color, outline=C["siyah"], width=3)


# -----------------------------------------------------------------------------
# Desen kompozisyonları
# -----------------------------------------------------------------------------

def pattern_car_tile() -> Image.Image:
    preview = new_rgb((230, 245, 255))
    draw = ImageDraw.Draw(preview)
    draw_tile_background(draw, tile_size=128, palette=[C["kobalt"], C["turkuaz"], C["yesil"], C["sari"], C["mor"], C["kirmizi"]])
    draw_racing_car(draw, SIZE // 2, SIZE // 2 + 30, scale=2.0)
    draw_iznik_border(draw, 30, C["kobalt"], width=6)
    draw_corner_flowers(draw, 30, C["yesil"])
    return preview


def pattern_dino_mandala() -> Image.Image:
    preview = new_rgb((240, 255, 240))
    draw = ImageDraw.Draw(preview)
    cx, cy = SIZE // 2, SIZE // 2
    for r in range(140, 420, 50):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C["yesil"], width=5)
    draw_radial_petals(draw, cx, cy, 380, 14, C["turkuaz"], width=5)
    draw_rosette(draw, cx, cy, 90, C["sari"], width=4)
    draw_dinosaur(draw, cx, cy + 20, scale=1.6)
    draw_iznik_border(draw, 35, C["yesil"], width=6)
    draw_corner_flowers(draw, 35, C["turkuaz"])
    return preview


def pattern_rocket_stars() -> Image.Image:
    preview = new_rgb((20, 30, 70))  # Gece mavisi
    draw = ImageDraw.Draw(preview)
    # Yıldızlar
    for _ in range(30):
        x = np.random.randint(60, SIZE - 60)
        y = np.random.randint(60, SIZE - 60)
        r = np.random.randint(3, 8)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=C["sari"])
    # Çini çerçeve
    draw_iznik_border(draw, 40, C["turkuaz"], width=6)
    draw_corner_flowers(draw, 40, C["sari"])
    # Roket
    draw_rocket(draw, SIZE // 2, SIZE // 2 - 60, scale=2.2)
    return preview


def pattern_soccer_mandala() -> Image.Image:
    preview = new_rgb((240, 255, 240))
    draw = ImageDraw.Draw(preview)
    cx, cy = SIZE // 2, SIZE // 2
    for r in range(120, 420, 55):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C["yesil"], width=5)
    draw_radial_petals(draw, cx, cy, 360, 12, C["beyaz"], width=5)
    draw_soccer_ball(draw, cx, cy, 130)
    draw_iznik_border(draw, 35, C["yesil"], width=6)
    draw_corner_flowers(draw, 35, C["siyah"])
    return preview


def pattern_butterfly_tile() -> Image.Image:
    preview = new_rgb((255, 240, 250))
    draw = ImageDraw.Draw(preview)
    draw_tile_background(draw, tile_size=128, palette=[C["pembe"], C["mor"], C["turkuaz"], C["sari"], C["kirmizi"], C["yesil"]])
    draw_butterfly(draw, SIZE // 2, SIZE // 2, scale=2.6)
    draw_iznik_border(draw, 30, C["mor"], width=6)
    draw_corner_flowers(draw, 30, C["pembe"])
    return preview


def pattern_unicorn_mandala() -> Image.Image:
    preview = new_rgb((255, 245, 255))
    draw = ImageDraw.Draw(preview)
    cx, cy = SIZE // 2, SIZE // 2
    for r in range(140, 430, 50):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C["mor"], width=5)
    draw_radial_petals(draw, cx, cy, 390, 16, C["pembe"], width=5)
    draw_rosette(draw, cx, cy, 80, C["sari"], width=4)
    draw_unicorn(draw, cx, cy + 50, scale=1.5)
    draw_iznik_border(draw, 35, C["mor"], width=6)
    draw_corner_flowers(draw, 35, C["pembe"])
    return preview


def pattern_princess_crown() -> Image.Image:
    preview = new_rgb((255, 248, 240))
    draw = ImageDraw.Draw(preview)
    # Arka plan yumuşak çiçek deseni (büyük yuvarlaklar)
    for i in range(6):
        x = ((i % 3) * 340) + 170
        y = ((i // 3) * 480) + 240
        draw.ellipse([x - 130, y - 130, x + 130, y + 130], fill=(255, 235, 245), outline=C["pembe"], width=3)
        draw_rosette(draw, x, y, 60, C["pembe"], width=3)
    draw_crown(draw, SIZE // 2, SIZE // 2 - 40, scale=2.2)
    draw_iznik_border(draw, 35, C["sari"], width=6)
    draw_corner_flowers(draw, 35, C["kirmizi"])
    return preview


def pattern_heart_mandala() -> Image.Image:
    preview = new_rgb((255, 240, 245))
    draw = ImageDraw.Draw(preview)
    cx, cy = SIZE // 2, SIZE // 2
    for r in range(130, 410, 50):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C["pembe"], width=5)
    draw_radial_petals(draw, cx, cy, 370, 12, C["kirmizi"], width=5)
    draw_heart_mandala_center(draw, cx, cy, 120, C["kirmizi"])
    draw_iznik_border(draw, 35, C["kirmizi"], width=6)
    draw_corner_flowers(draw, 35, C["pembe"])
    return preview


# -----------------------------------------------------------------------------
# Mevcut desenleri işle
# -----------------------------------------------------------------------------

def process_existing() -> None:
    """
    Önceden var olan 512x512 preview görsellerini 1024x1024'e upscale eder
    ve her biri için optimize edilmiş line-art üretir.
    """
    previews = [
        ("preview_iznik_tile", {"canny_low": 50, "canny_high": 150, "dilation_size": 3, "dilation_iterations": 2, "min_component_size": 30}),
        ("preview_iznik_vase", {"canny_low": 50, "canny_high": 150, "dilation_size": 3, "dilation_iterations": 2, "min_component_size": 30}),
        ("preview_flower", {"canny_low": 40, "canny_high": 120, "dilation_size": 3, "dilation_iterations": 2, "min_component_size": 25}),
        # Geometrik desen çok küçük karolardan oluştuğu için Canny fazla detay üretiyor.
        # Eski FIND_EDGES yöntemi bu desen için daha sade sonuç veriyor.
        ("preview_geometric", {"use_legacy_edges": True, "canny_low": 60, "dilation_size": 3, "min_component_size": 20}),
    ]

    for name, lineart_kwargs in previews:
        src = OUT_DIR / f"{name}.png"
        if src.exists():
            backup = OUT_DIR / f"{name}_512.png"
            src.rename(backup)
            upscale_preview(backup, src)
            print(f"  Upscaled preview: {name}.png")
            # Lineart'ı preview'dan yeniden üret
            line_name = name.replace("preview_", "lineart_")
            preview_img = Image.open(src)
            preview_to_lineart(preview_img, **lineart_kwargs).save(OUT_DIR / f"{line_name}.png")
            print(f"  Regenerated lineart: {line_name}.png")


# -----------------------------------------------------------------------------
# Ana akış
# -----------------------------------------------------------------------------

def main() -> None:
    print(f"[generate_assets] Çıktı dizini: {OUT_DIR}")

    process_existing()

    patterns = [
        ("car_tile", pattern_car_tile),
        ("dino_mandala", pattern_dino_mandala),
        ("rocket_stars", pattern_rocket_stars),
        ("soccer_mandala", pattern_soccer_mandala),
        ("butterfly_tile", pattern_butterfly_tile),
        ("unicorn_mandala", pattern_unicorn_mandala),
        ("princess_crown", pattern_princess_crown),
        ("heart_mandala", pattern_heart_mandala),
    ]

    # Programatik desenler düz renkli olduğu için daha kalın, temiz hatlar
    procedural_lineart_kwargs = {
        "canny_low": 50,
        "canny_high": 150,
        "dilation_size": 4,
        "dilation_iterations": 2,
        "min_component_size": 35,
    }

    for name, gen in patterns:
        preview = gen()
        preview.save(OUT_DIR / f"preview_{name}.png")
        preview_to_lineart(preview, **procedural_lineart_kwargs).save(OUT_DIR / f"lineart_{name}.png")
        print(f"  Generated: preview_{name}.png, lineart_{name}.png")

    # Cleanup backups
    for f in OUT_DIR.glob("*_512.png"):
        f.unlink()
        print(f"  Removed backup: {f.name}")

    print("[generate_assets] Tamamlandı.")


if __name__ == "__main__":
    main()
