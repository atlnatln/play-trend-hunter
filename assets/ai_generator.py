#!/usr/bin/env python3
"""
Play Trend Hunter — AI Asset Generator (FLUX.1-schnell)
Uses FLUX.1-schnell via diffusers for high-quality app assets.
License: Apache 2.0 (free for commercial use)
VRAM: ~8-10GB with model_cpu_offload, safer with sequential_cpu_offload
"""
import torch
from diffusers import FluxPipeline
from pathlib import Path

# Lazy-load pipeline
_pipe = None


def _get_pipeline():
    global _pipe
    if _pipe is None:
        print("[AI] Loading FLUX.1-schnell...")
        _pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.float16,
            local_files_only=True,
        )
        # Sequential offload is slower but safer for 12GB VRAM
        _pipe.enable_sequential_cpu_offload()
        _pipe.vae.enable_slicing()
        print("[AI] Pipeline ready")
    return _pipe


def generate_image(prompt: str, output_path: Path, width: int = 512, height: int = 512):
    """Generate a single image from text prompt using FLUX-schnell."""
    pipe = _get_pipeline()
    image = pipe(
        prompt,
        width=width,
        height=height,
        num_inference_steps=4,      # schnell only needs 4 steps
        guidance_scale=0.0,         # schnell uses cfg=0
        max_sequence_length=256,
    ).images[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def generate_app_icon(app_name: str, category: str, output_path: Path = None):
    """Generate a 1024x1024 app icon (downscale to 512x512 after if needed)."""
    if output_path is None:
        slug = app_name.lower().replace(" ", "_")
        output_path = Path("assets/output") / slug / f"{slug}_ai_icon.png"

    prompt = (
        f"A professional mobile app launcher icon for a {category.lower().replace('_', ' ')} app, "
        "flat vector design, minimal, clean solid background, "
        "centered composition, no text, no letters, no words, "
        "app store ready, high quality"
    )
    return generate_image(prompt, output_path, width=512, height=512)


def generate_feature_graphic(app_name: str, category: str, output_path: Path = None):
    """Generate a 1024x500 Google Play feature graphic."""
    if output_path is None:
        slug = app_name.lower().replace(" ", "_")
        output_path = Path("assets/output") / slug / f"{slug}_ai_feature.png"

    prompt = (
        f"A wide promotional banner background for a {category.lower().replace('_', ' ')} mobile app, "
        "vibrant modern design, abstract gradient background, "
        "professional app store feature graphic, "
        "no text, no letters, no words, no logos, no buttons, "
        "clean background with empty space on the right side"
    )
    return generate_image(prompt, output_path, width=1024, height=512)


def generate_ai_assets(app_name: str, category: str) -> dict[str, Path]:
    """Generate full Play Store asset set: 1024x1024 icon + 1024x500 feature graphic."""
    from assets.ai_postprocess import add_text_to_feature_graphic, upscale_icon

    slug = app_name.lower().replace(" ", "_")
    out_dir = Path("assets/output") / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    icon_raw = out_dir / f"{slug}_ai_icon.png"
    feature_raw = out_dir / f"{slug}_ai_feature.png"
    icon_final = out_dir / f"{slug}_ai_icon_1024.png"
    feature_final = out_dir / f"{slug}_ai_feature_1024x500.png"

    generate_app_icon(app_name, category, icon_raw)
    upscale_icon(icon_raw, icon_final, size=1024)
    generate_feature_graphic(app_name, category, feature_raw)
    add_text_to_feature_graphic(feature_raw, app_name, category, feature_final)

    return {
        "icon_512": icon_raw,
        "icon_1024": icon_final,
        "feature_raw": feature_raw,
        "feature_final": feature_final,
    }


if __name__ == "__main__":
    import time
    t0 = time.time()
    out = generate_app_icon("Digital Compass", "MAPS_AND_NAVIGATION")
    print(f"Icon generated: {out} ({time.time() - t0:.1f}s)")
