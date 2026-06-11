#!/usr/bin/env python3
"""
Çini Boyama line-art pipeline test aracı.

Mevcut generate_assets.py'deki preview_to_lineart() fonksiyonunu ve yeni
OpenCV tabanlı alternatifleri karşılaştırır. Çıktılar tools/lineart_tests/
dizinine kaydedilir.

Gereksinimler:
    source /home/akn/local/uygulama-gelistir-play/.venv/bin/activate
    python tools/test_lineart_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# uygulama-gelistir-play .venv kullanıyoruz; Pillow/numpy/scipy/opencv orada
sys.path.insert(0, str(Path("/home/akn/local/uygulama-gelistir-play")))

import cv2
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parent.parent
DRAWABLE_DIR = ROOT / "app/src/main/res/drawable-nodpi"
OUT_DIR = ROOT / "tools" / "lineart_tests"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Mevcut pipeline (generate_assets.py'den kopya)
# ---------------------------------------------------------------------------
def preview_to_lineart_legacy(img: Image.Image, threshold: int = 40, dilation_size: int = 3, min_size: int = 12) -> Image.Image:
    gray = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    arr = np.array(edges)
    dilated = ndimage.grey_dilation(arr, size=(dilation_size, dilation_size))
    binary = dilated > threshold
    labeled, num = ndimage.label(binary)
    sizes = ndimage.sum(binary, labeled, range(1, num + 1))
    mask = np.concatenate(([False], sizes >= min_size))
    binary = mask[labeled]
    out = (np.where(binary, 0, 255)).astype(np.uint8)
    return Image.fromarray(out, "L")


# ---------------------------------------------------------------------------
# Yeni pipeline v1: Canny edge + morfolojik kalınlaştırma + gürültü temizliği
# ---------------------------------------------------------------------------
def preview_to_lineart_v1(img: Image.Image, size: int = 1024) -> Image.Image:
    # 1. Grayscale
    gray = np.array(img.convert("L"))

    # 2. Hafif blur (gürültü azaltma)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Kontrast artırma (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)

    # 4. Canny edge detection
    edges = cv2.Canny(enhanced, 50, 150)

    # 5. Hatları kalınlaştır (dilate)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    thick = cv2.dilate(edges, kernel, iterations=2)

    # 6. Küçük gürültüleri temizle (connected components)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thick, connectivity=8)
    cleaned = np.zeros_like(thick)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 30:  # çok küçük noktaları at
            cleaned[labels == i] = 255

    # 7. Beyaz arka plan, siyah hatlar
    out = 255 - cleaned
    return Image.fromarray(out, "L")


# ---------------------------------------------------------------------------
# Yeni pipeline v2: Adaptive threshold + closing (kapalı bölgeler için)
# ---------------------------------------------------------------------------
def preview_to_lineart_v2(img: Image.Image, size: int = 1024) -> Image.Image:
    gray = np.array(img.convert("L"))

    # Yumuşatma
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold: her bölge için ayrı eşik
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=15,
        C=5
    )

    # Invert edip kenarları almak için Canny de ekleyelim
    edges = cv2.Canny(blurred, 40, 120)
    combined = cv2.bitwise_or(binary, edges)

    # Hatları kalınlaştır
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    thick = cv2.dilate(combined, kernel, iterations=2)

    # Küçük delikleri kapat (closing) - kapanmayan hatlar için
    closed = cv2.morphologyEx(thick, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Gürültü temizliği
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    cleaned = np.zeros_like(closed)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 25:
            cleaned[labels == i] = 255

    out = 255 - cleaned
    return Image.fromarray(out, "L")


# ---------------------------------------------------------------------------
# Yeni pipeline v3: V1 + daha agresif kalınlaştırma (çocuklar için)
# ---------------------------------------------------------------------------
def preview_to_lineart_v3(img: Image.Image, size: int = 1024) -> Image.Image:
    gray = np.array(img.convert("L"))
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    edges = cv2.Canny(enhanced, 50, 150)

    # Daha büyük kernel ve daha fazla iteration = daha kalın hatlar
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thick = cv2.dilate(edges, kernel, iterations=2)

    # Closing ile küçük boşlukları kapat
    closed = cv2.morphologyEx(thick, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Gürültü temizliği (biraz daha toleranslı)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    cleaned = np.zeros_like(closed)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 40:
            cleaned[labels == i] = 255

    out = 255 - cleaned
    return Image.fromarray(out, "L")


# ---------------------------------------------------------------------------
# Yeni pipeline v4: Canny + skeletonization + kalınlaştırma
# (çift konturları tek, düzgün hat haline getirir)
# ---------------------------------------------------------------------------
def preview_to_lineart_v4(img: Image.Image, size: int = 1024) -> Image.Image:
    gray = np.array(img.convert("L"))
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    edges = cv2.Canny(enhanced, 50, 150)

    # Skeletonize: kalın çift hatları tek piksel merkez çizgisine indir
    skel = skeletonize(edges > 0).astype(np.uint8) * 255

    # Şimdi tek hatları istenen kalınlıkta aç
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
    thick = cv2.dilate(skel, kernel, iterations=2)

    # Küçük gürültüleri temizle
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thick, connectivity=8)
    cleaned = np.zeros_like(thick)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 35:
            cleaned[labels == i] = 255

    out = 255 - cleaned
    return Image.fromarray(out, "L")


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
PREVIEW_FILES = [
    "preview_iznik_tile.png",
    "preview_flower.png",
    "preview_geometric.png",
    "preview_iznik_vase.png",
]


def main() -> None:
    print(f"[test_lineart] Çıktı dizini: {OUT_DIR}")
    pipelines = [
        ("legacy", preview_to_lineart_legacy),
        ("v1_canny", preview_to_lineart_v1),
        ("v2_adaptive", preview_to_lineart_v2),
        ("v3_bold", preview_to_lineart_v3),
        ("v4_skeleton", preview_to_lineart_v4),
    ]

    for filename in PREVIEW_FILES:
        src = DRAWABLE_DIR / filename
        if not src.exists():
            print(f"  [SKIP] {filename} bulunamadı")
            continue

        print(f"  İşleniyor: {filename}")
        img = Image.open(src).convert("RGB")

        # Mevcut üretim akışı gibi: preview'u 1024'e upscale et
        img_1024 = img.resize((1024, 1024), Image.Resampling.LANCZOS)

        for name, fn in pipelines:
            out = fn(img_1024)
            out_path = OUT_DIR / f"{src.stem}_{name}.png"
            out.save(out_path)
            print(f"    -> {out_path.name}")

    print("[test_lineart] Tamamlandı.")


if __name__ == "__main__":
    main()
