---
name: vlm-screenshot
description: Android screenshot analizi icin qwen2.5vl:7b VLM kullanimi
metadata:
  last_updated: 2026-06-03
  model: "qwen2.5vl:7b"
  model_size: "6.0GB"
  ollama_version: "latest"
  benchmark_ref: "docs/vlm-benchmark/2026-06-02-results.md"
---

# VLM Screenshot Analizi — Teknik Referans

> Ana proje: `play-trend-hunter` skill. Android test: `android-test-pipeline` skill.

---

## 1. Seçilen Model: qwen2.5vl:7b

**Neden qwen2.5vl:7b?**

| Model | OCR | Türkçe | Hayal Ürünü | Skor |
|-------|-----|--------|-------------|------|
| llava-phi3 | ❌ | ❌ | ❌ | 0/25 |
| llava | ⚠️ | ❌ | ❌ | 1/25 |
| llava-llama3 | ❌ | ❌ | ❌ | 0/25 |
| llama3.2-vision | ⚠️ | ⚠️ | ⚠️ | 11/25 |
| minicpm-v | ⚠️ | ⚠️ | ✅ | 16/25 |
| **qwen2.5vl:7b** | ✅ | ✅ | ✅ | **25/25** |

*qwen2.5vl:7b 5/5 senaryoda mükemmel OCR, Türkçe karakterleri (ş,ç,ı,ğ,ü,ö) doğru okuyor, hayal ürünü eleman üretmiyor.*

**Detaylı benchmark:** `docs/vlm-benchmark/2026-06-02-results.md`

---

## 2. Ne Zaman VLM Kullanılır?

| Durum | Kullan? | Amaç |
|-------|---------|------|
| **Smoke test sonrası** | ✅ | Ekran beklendiği gibi mi? Metinler doğru mu? |
| **Maestro assertion başarısız** | ✅ | UI element neden bulunamadı? Ekranda ne var? |
| **App crash sonrası** | ✅ | Crash sonrası ekran durumu nedir? |
| **Yeni app build sonrası** | ✅ | İlk açılış ekranı doğru render edilmiş mi? |
| **Renk/estetik değerlendirme** | ❌ | Agent VLM ile renk yorumu yapabilir ama "güzel mi?" kararı kullanıcıya bırakılır |
| **Animasyon/oyun mekaniği** | ❌ | VLM tek frame analiz eder, akıcılık/oyun deneyimi değerlendirilemez |
| **Video/frame dizisi** | ⚠️ | Her frame ayrı analiz edilir. 30-40 frame = ~4.5-6 dk. Frame küçültme önerilir. |

---

## 3. VLM Kullanım Akışı

```bash
# 1. Screenshot al
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png /tmp/screen.png

# 2. Base64'e çvir
IMG_B64=$(base64 -w 0 /tmp/screen.png)

# 3. qwen2.5vl:7b'e gönder
curl -s http://localhost:11434/api/generate -d "$(jq -n \
  --arg img "$IMG_B64" \
  '{model: "qwen2.5vl:7b",
    prompt: "Read all text in this Android screenshot. Describe UI elements, colors, and layout.",
    images: [$img],
    stream: false,
    options: {temperature: 0.1}}')"
```

**Prompt stratejisi:**
- `temperature: 0.1` — Tutarlı, tekrarlanabilir sonuçlar
- Spesifik sorular sor — "How many buttons?" genel "Describe"'den daha doğru
- Türkçe metin varsa prompt'ta belirtme gerekmez, model otomatik tanır

---

## 4. Performans Beklentisi

| Metric | Değer |
|--------|-------|
| **Tek screenshot** | ~8-10 saniye |
| **30-40 frame (video)** | ~4.5-6 dakika |
| **VRAM kullanımı** | ~7-8GB |
| **Model boyutu** | 6.0GB disk |
| **Frame küçültme** | 640×360'a küçültmek süreyi yarıya indirir |

---

## 5. Ollama Kurulumu

```bash
# Modeli indir (tek seferlik)
ollama pull qwen2.5vl:7b

# Diğer VLM modelleri sil (benchmark sonrası temizlik)
# ollama rm llava-phi3 llava llava-llama3 llama3.2-vision minicpm-v

# Çalıştır
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5vl:7b",
  "prompt": "...",
  "images": ["..."],
  "stream": false
}'
```

> **Not:** Ollama daemon çalışıyor olmalı (`ollama serve`).
