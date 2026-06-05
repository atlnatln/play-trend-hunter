#!/usr/bin/env python3
"""
Play Trend Hunter — AI Asset Post-processing
Adds crisp text overlays to FLUX-generated backgrounds.
Resizes/crops to exact Play Store dimensions.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _find_font(size: int) -> ImageFont.FreeTypeFont:
    """Find a usable TrueType font on the system."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
        "C:/Windows/Fonts/arialbd.ttf",  # Windows fallback
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def crop_to_feature_graphic(image: Image.Image) -> Image.Image:
    """Crop 1024x512 (or close) to exact 1024x500 Play Store size."""
    if image.size == (1024, 500):
        return image
    # Center-crop vertically: keep the middle 500px of 512px height
    if image.height >= 500:
        top = (image.height - 500) // 2
        return image.crop((0, top, 1024, top + 500))
    # Fallback resize if smaller
    return image.resize((1024, 500), Image.Resampling.LANCZOS)


def add_text_to_feature_graphic(
    input_path: Path,
    app_name: str,
    category: str,
    output_path: Path = None,
) -> Path:
    """Overlay app name + tagline on the right side of a feature graphic."""
    img = Image.open(input_path).convert("RGB")
    img = crop_to_feature_graphic(img)

    draw = ImageDraw.Draw(img)
    title_font = _find_font(56)
    tag_font = _find_font(26)

    # Place text on the right half with padding
    x = 420
    y_title = 180
    y_tag = 260

    # Determine text color by sampling background brightness
    sample = img.crop((x, y_title - 40, x + 400, y_tag + 60))
    pixels = list(sample.convert("L").getdata())
    avg = sum(pixels) / len(pixels)
    color = "black" if avg > 160 else "white"

    draw.text((x, y_title), app_name, font=title_font, fill=color)
    tagline = category.replace("_", " ").title()
    draw.text((x, y_tag), tagline, font=tag_font, fill=color)

    if output_path is None:
        slug = app_name.lower().replace(" ", "_")
        output_path = Path("assets/output") / slug / f"{slug}_ai_feature_final.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path


def upscale_icon(input_path: Path, output_path: Path = None, size: int = 1024) -> Path:
    """Upscale a 512x512 icon to Play Store required 1024x1024."""
    img = Image.open(input_path).convert("RGB")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    if output_path is None:
        output_path = input_path.with_suffix(".upscaled.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path


if __name__ == "__main__":
    import sys
    app = sys.argv[1] if len(sys.argv) > 1 else "Digital Compass"
    cat = sys.argv[2] if len(sys.argv) > 2 else "MAPS_AND_NAVIGATION"
    slug = app.lower().replace(" ", "_")
    base = Path("assets/output") / slug
    out = add_text_to_feature_graphic(
        base / f"{slug}_ai_feature.png", app, cat
    )
    print(f"Post-processed: {out}")
