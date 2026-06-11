#!/usr/bin/env python3
"""
cini-boyama — FLUX Line-Art Generator
Uses uygulama-gelistir-play's FLUX.2-dev GGUF pipeline to generate
coloring-book style line-art images for Turkish Iznik tile patterns.

Post-process: OpenCV threshold + morphological closing for guaranteed
closed regions suitable for flood-fill coloring apps.

VRAM: ~10GB via max_vram=10, hybrid GPU+RAM mode.
Typical speed: 75-120s per 1024x1024 image (RTX 4070 12GB).
"""
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import stable-diffusion-cpp-python from uygulama-gelistir-play venv
# ---------------------------------------------------------------------------
UGP_ROOT = Path("/home/akn/local/uygulama-gelistir-play")
UGP_VENV = UGP_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"

if str(UGP_VENV) not in sys.path:
    sys.path.insert(0, str(UGP_VENV))

from stable_diffusion_cpp import StableDiffusion
import cv2
import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Model paths (shared with uygulama-gelistir-play)
# ---------------------------------------------------------------------------
MODELS_DIR = UGP_ROOT / "models"
GGUF_FLUX_PATH = MODELS_DIR / "flux2-dev-Q4_K_M.gguf"
VAE_PATH = MODELS_DIR / "ae.safetensors"
LLM_PATH = MODELS_DIR / "Mistral-Small-3.2-24B-Instruct-2506-Q4_K_M.gguf"

# ---------------------------------------------------------------------------
# Cached pipeline
# ---------------------------------------------------------------------------
_pipeline: StableDiffusion | None = None


def _get_pipeline() -> StableDiffusion:
    """Load (or reuse) the FLUX.2-dev GGUF pipeline."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    for p in (GGUF_FLUX_PATH, VAE_PATH, LLM_PATH):
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: {p}")

    print("[FLUX] Loading pipeline...")
    print(f"[FLUX]   Diffusion: {GGUF_FLUX_PATH}")
    print(f"[FLUX]   VAE:       {VAE_PATH}")
    print(f"[FLUX]   LLM:       {LLM_PATH}")

    _pipeline = StableDiffusion(
        diffusion_model_path=str(GGUF_FLUX_PATH),
        vae_path=str(VAE_PATH),
        llm_path=str(LLM_PATH),
        offload_params_to_cpu=True,
        diffusion_flash_attn=True,
        max_vram=10,
    )
    print("[FLUX] Pipeline ready")
    return _pipeline


# ---------------------------------------------------------------------------
# Prompts — optimized for line-art / coloring book output
# ---------------------------------------------------------------------------
LINEART_PROMPTS = {
    "iznik_vase": (
        "A traditional Turkish Iznik ceramic vase, line art illustration, "
        "coloring book page for adults, black and white, thick bold outlines, "
        "closed boundaries, clean crisp lines, no shading, no gradient, no color, "
        "no gray, no photo, no realistic, no shadow, floral and leaf ornament patterns, "
        "symmetrical design, white background, high contrast, 300 DPI, vector-style"
    ),
    "iznik_tile": (
        "A traditional Turkish Iznik tile pattern, geometric floral mosaic, "
        "line art illustration, coloring book page, black and white, "
        "thick bold outlines, closed boundaries, clean crisp lines, "
        "no shading, no gradient, no color, no gray, symmetrical repeating pattern, "
        "white background, high contrast, vector-style"
    ),
    "flower": (
        "A beautiful stylized flower bouquet, line art illustration, "
        "coloring book page, black and white, thick bold outlines, "
        "closed boundaries, clean crisp lines, no shading, no gradient, "
        "no color, no gray, decorative ornamental style, white background, "
        "high contrast, vector-style"
    ),
    "geometric": (
        "An Islamic geometric star and polygon pattern, line art illustration, "
        "coloring book page, black and white, thick bold outlines, "
        "closed boundaries, clean crisp lines, no shading, no gradient, "
        "no color, no gray, symmetrical tessellation, white background, "
        "high contrast, vector-style"
    ),
    "mandala": (
        "A decorative mandala design, line art illustration, coloring book page, "
        "black and white, thick bold outlines, closed boundaries, "
        "clean crisp lines, no shading, no gradient, no color, no gray, "
        "radial symmetry, white background, high contrast, vector-style"
    ),
}


def generate_flux_lineart(
    prompt: str,
    output_path: Path,
    width: int = 1024,
    height: int = 1024,
    sample_steps: int = 20,
    seed: int = 42,
) -> Path:
    """Generate a raw image from FLUX using the given prompt."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sd = _get_pipeline()
    image = sd.generate_image(
        prompt=prompt,
        width=width,
        height=height,
        sample_steps=sample_steps,
        cfg_scale=1.0,
        sample_method="euler",
        seed=seed,
    )
    if isinstance(image, list):
        image = image[0]
    image.save(output_path)
    return output_path


def postprocess_to_lineart(
    input_path: Path,
    output_path: Path,
    blur_kernel: int = 3,
    threshold_value: int = 200,
    dilate_kernel: int = 2,
    dilate_iterations: int = 1,
) -> Path:
    """
    Light post-process for FLUX-generated line-art.

    FLUX already outputs clean black-and-white line art.
    We only need to:
      1. Convert to grayscale
      2. Threshold to ensure pure black/white (no gray anti-aliasing)
      3. Slight dilation to thicken lines for robust flood-fill
    """
    img = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image: {input_path}")

    # 1. Light blur to reduce anti-aliasing artifacts
    blurred = cv2.GaussianBlur(img, (blur_kernel, blur_kernel), 0)

    # 2. Simple threshold: everything darker than 200 becomes black (0)
    #    lighter becomes white (255)
    _, binary = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # 3. Dilation: thicken lines slightly for robust flood-fill barriers
    if dilate_kernel > 0 and dilate_iterations > 0:
        kernel = np.ones((dilate_kernel, dilate_kernel), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=dilate_iterations)

    # 4. Invert back: black lines (0) on white background (255)
    final = cv2.bitwise_not(binary)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), final)
    return output_path


def generate_and_process(
    pattern_key: str,
    output_dir: Path,
    width: int = 1024,
    height: int = 1024,
    sample_steps: int = 20,
    seed: int = 42,
    keep_raw: bool = False,
) -> dict[str, Path]:
    """
    Full pipeline: FLUX generation -> OpenCV post-process -> line-art PNG.

    Returns dict with 'raw' and 'lineart' paths.
    """
    if pattern_key not in LINEART_PROMPTS:
        raise KeyError(f"Unknown pattern '{pattern_key}'. Available: {list(LINEART_PROMPTS.keys())}")

    prompt = LINEART_PROMPTS[pattern_key]
    raw_path = output_dir / f"flux_raw_{pattern_key}.png"
    lineart_path = output_dir / f"lineart_{pattern_key}_flux.png"

    print(f"\n[GEN] Pattern: {pattern_key}")
    print(f"[GEN] Prompt: {prompt[:100]}...")

    import time
    t0 = time.time()
    generate_flux_lineart(prompt, raw_path, width, height, sample_steps, seed)
    print(f"[GEN] FLUX raw saved: {raw_path} ({time.time() - t0:.1f}s)")

    t1 = time.time()
    postprocess_to_lineart(raw_path, lineart_path)
    print(f"[GEN] Line-art saved: {lineart_path} ({time.time() - t1:.1f}s)")

    if not keep_raw:
        raw_path.unlink()
        print(f"[GEN] Raw cleaned up")

    return {"lineart": lineart_path}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate FLUX line-art for cini-boyama")
    parser.add_argument("pattern", choices=list(LINEART_PROMPTS.keys()), help="Pattern to generate")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "flux_outputs", help="Output directory")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--steps", type=int, default=20, help="Sampling steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--keep-raw", action="store_true", help="Keep raw FLUX output")
    args = parser.parse_args()

    result = generate_and_process(
        args.pattern,
        args.output_dir,
        args.width,
        args.height,
        args.steps,
        args.seed,
        args.keep_raw,
    )
    print(f"\n✅ Done: {result['lineart']}")
