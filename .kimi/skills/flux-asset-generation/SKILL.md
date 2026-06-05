---
name: flux-asset-generation
description: |
  Play Store app asset üretimi için FLUX.1-schnell pipeline'ı.
  Icon (512x512 / 1024x1024) ve feature graphic (1024x500) üretir.
  RTX 4070 12GB VRAM ile sequential CPU offload kullanır.
  Activate when user says "ai asset", "flux asset", "play store image",
  "app icon generate", "feature graphic generate", or modifies assets/ai_generator.py.
metadata:
  last_updated: 2026-06-05
  maintainer: kimi-agent
---

# FLUX Asset Generation

> **Scope:** Play Trend Hunter projesi (`projects/play-trend-hunter/`).
> **Lokasyon:** `assets/ai_generator.py`, `assets/ai_postprocess.py`, `run.py ai-assets`.
> **Lisans:** FLUX.1-schnell — Apache 2.0 (ticari kullanım serbest).

---

## 1. Ne Zaman Kullanılır?

| Senaryo | Kullanılan Araç | Neden? |
|---------|----------------|--------|
| **Hızlı placeholder / test** | `run.py assets <app> <cat>` (PIL) | 0.5 sn, deterministik, offline. Kalite düşük ama yeterli. |
| **Gerçek Play Store yayını** | `run.py ai-assets <app> <cat>` (FLUX) | 40-80 sn, yüksek kalite, AI üretimi. |
| **Toplu batch üretimi** | `assets/ai_generator.py` API'si | Birden fazla app için döngü. |

**Kural:** Üretim öncesi (Faz 1+) Play Store görselleri FLUX ile üretilir. Faz 0'da analiz ve hızlı iterasyon için PIL generator yeterlidir.

---

## 2. Teknik Önkoşullar

### Donanım
- **GPU:** NVIDIA RTX 4070 12GB VRAM (test edilmiş).
- **RAM:** En az 24GB sistem RAM önerilir (model ~25GB cache + CPU offload).
- **Disk:** ~54GB Hugging Face cache alanı.

### Bağımlılıklar
```text
# requirements.txt
torch>=2.0.0
torchvision>=0.15.0
diffusers>=0.30.0
transformers>=4.40.0,<5.0
accelerate>=0.30.0
Pillow>=10.0.0
protobuf
sentencepiece
```

> **Önemli:** `transformers>=5.0` ile `diffusers 0.38` uyumsuz (`CLIPImageProcessor` hatası). `<5.0` zorunlu.
> **Önemli:** FLUX'un T5 tokenizer'ı `protobuf` ve `sentencepiece` gerektirir. Eksikse `ImportError`/`ValueError` verir.

### Model Cache
```bash
# İlk kurulumda indir (~54GB, 1-2 saat sürebilir)
cd projects/play-trend-hunter
source .venv/bin/activate
huggingface-cli download black-forest-labs/FLUX.1-schnell --resume-download
```

Cache lokasyonu: `~/.cache/huggingface/hub/models--black-forest-labs--FLUX.1-schnell/`

---

## 3. CLI Kullanımı

```bash
cd projects/play-trend-hunter
source .venv/bin/activate

python run.py ai-assets "Digital Compass" "MAPS_AND_NAVIGATION"
```

**Çıktılar** (`assets/output/<slug>/`):
| Dosya | Boyut | Amaç |
|-------|-------|------|
| `<slug>_ai_icon.png` | 512×512 | Ham AI icon |
| `<slug>_ai_icon_1024.png` | 1024×1024 | Play Store yüksek çözünürlük iconu |
| `<slug>_ai_feature.png` | 1024×512 | Ham AI feature arka planı |
| `<slug>_ai_feature_1024x500.png` | 1024×500 | Final Play Store feature graphic |

**Toplam süre:** ~40-80 saniye (pipeline loaded ise).

---

## 4. Python API Kullanımı

```python
from assets.ai_generator import generate_ai_assets

paths = generate_ai_assets("Digital Compass", "MAPS_AND_NAVIGATION")
# paths["icon_512"]      -> 512x512 icon
# paths["icon_1024"]     -> upscaled 1024x1024 icon
# paths["feature_raw"]   -> 1024x512 background
# paths["feature_final"] -> 1024x500 with text overlay
```

Tek tek fonksiyonlar:
```python
from assets.ai_generator import generate_app_icon, generate_feature_graphic
from assets.ai_postprocess import upscale_icon, add_text_to_feature_graphic

icon_raw = generate_app_icon("App Name", "CATEGORY")
icon_1024 = upscale_icon(icon_raw, size=1024)

feature_raw = generate_feature_graphic("App Name", "CATEGORY")
feature_final = add_text_to_feature_graphic(feature_raw, "App Name", "CATEGORY")
```

---

## 5. Prompt Stratejisi

FLUX-schnell **metin render etmede kötüdür** (uydurma yazılar, bozuk fontlar). Bu yüzden:

- Icon prompt: `no text, no letters, no words` zorunlu.
- Feature prompt: `no text, no letters, no words, no logos, no buttons` zorunlu.
- App ismi sonradan `assets/ai_postprocess.py` ile PIL overlay olarak eklenir.

**Örnek doğru prompt (feature):**
```
A wide promotional banner background for a maps and navigation mobile app,
vibrant modern design, abstract gradient background,
professional app store feature graphic,
no text, no letters, no words, no logos, no buttons,
clean background with empty space on the right side
```

---

## 6. VRAM Yönetimi

`assets/ai_generator.py` içinde şu ayarlar aktif:

```python
_pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell",
    torch_dtype=torch.float16,
    local_files_only=True,
)
_pipe.enable_sequential_cpu_offload()  # 12GB VRAM'a sığdırır
_pipe.vae.enable_slicing()
```

| Ayar | Etki |
|------|------|
| `torch.float16` | Bellek yarıya iner, bfloat16'a göre daha stabil |
| `enable_sequential_cpu_offload()` | Katmanları tek tek GPU'ya taşır. Yavaş ama güvenli |
| `vae.enable_slicing()` | VAE decode'u parçalı yapar |
| `local_files_only=True` | HF'e tekrar bağlanmaz, offline çalışır |

**Hatalı ayar:** `enable_model_cpu_offload()` 1024×1024'te CUDA OOM verir. `sequential_cpu_offload()` kullan.

---

## 7. Post-processing Akışı

`assets/ai_postprocess.py` şunları yapar:

1. **Feature graphic crop:** 1024×512 → 1024×500 (orta kısımdan crop).
2. **Text overlay:** Sağ tarafa app ismi (56px) + kategori (26px) ekler.
3. **Kontrast:** Arka plan parlaklığına göre otomatik beyaz/siyah renk seçer.
4. **Icon upscale:** 512×512 → 1024×1024 Lanczos resize.

---

## 8. Troubleshooting

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `ImportError: protobuf` | Eksik bağımlılık | `pip install protobuf sentencepiece` |
| `ValueError: Cannot instantiate this tokenizer` | `sentencepiece` eksik | `pip install sentencepiece` |
| `CUDA out of memory` | `model_cpu_offload` + 1024×1024 | `sequential_cpu_offload()` kullan, `float16` kullan |
| `FileNotFoundError: text_encoder_2` | Cache bozuk/yarım | `huggingface-cli download --resume-download` tekrar çalıştır |
| Uydurma yazılar (`Gogl Stare`) | Prompt'ta `no text` yok | Prompta `no text, no letters, no words` ekle |
| Yavaş ilk yükleme | ~54GB model diskten okunuyor | Normal. Sonraki çağrılar hızlı. |

---

## 9. Alternatifler

| Alternatif | Durum |
|------------|-------|
| **Ollama `x/flux2-klein`** | ❌ Linux'ta desteklenmiyor (sadece macOS). |
| **SDXL (HF diffusers)** | ⚠️ 6.9GB+ indirme, aynı VRAM sorunları. |
| **PIL generator (`assets/generator.py`)** | ✅ Hızlı, deterministik, düşük kalite. Faz 0 için yeterli. |

---

## 10. Dosya Referansı

```
assets/
├── ai_generator.py      # FLUX pipeline + generate_* fonksiyonları
├── ai_postprocess.py    # Crop, resize, text overlay
├── generator.py         # PIL tabanlı hızlı generator
└── output/<slug>/       # Üretilen görseller
```
