# Çini Boyama — Teknik Ortam Belgesi

## Dil ve Sürüm

- **Dil:** Kotlin
- **Min SDK:** 26 (Android 8.0)
- **Target SDK:** 35
- **Compile SDK:** 35

## Framework ve Kütüphaneler

| Kategori | Seçim | Versiyon |
|----------|-------|----------|
| UI Framework | Android ViewSystem (XML) | — |
| Layout | ConstraintLayout + RecyclerView | 2.1.4 |
| Theme | Material 3 (Dynamic color yok) | 1.11.0 |
| Test | JUnit + Espresso + Maestro | — |

## Asset Üretim Araçları

| Araç | Amaç | Notlar |
|------|------|--------|
| `tools/generate_assets.py` | Preview + line-art üretimi | OpenCV tabanlı Canny edge + dilation |
| `tools/test_lineart_pipeline.py` | Farklı line-art algoritmalarını karşılaştırma | Geliştirme/test amaçlı |

Python bağımlılıkları için:

```bash
source /home/akn/local/uygulama-gelistir-play/.venv/bin/activate
# veya: pip install -r requirements.txt
```

## Deploy Modeli

- Local debug build: `./gradlew assembleDebug`
- Release: `./gradlew assembleRelease` + keystore
- Maestro: `maestro test maestro/`
- Asset yenileme: `python tools/generate_assets.py`

## Yasaklı Kütüphaneler

| Kütüphane | Neden Yasak | Alternatif |
|-----------|-------------|------------|
| Glide / Coil | MVP'de bitmap ihtiyacı yok, gömülü drawable yeterli | — |
| Üçüncü parti reklam SDK | MVP kapsamında reklam yok | — |

## Örnek Kod Kalıpları

```kotlin
// Toleranslı flood fill: anti-aliased veya kapanmamış ince hatlarda
// komşu boyanabilir bölgeyi bularak boyamaya devam eder.
private fun floodFill(bitmap: Bitmap, x: Int, y: Int, color: Int): Int {
    // Hat üzerine dokunulduysa en yakın boş bölgeyi bul
    // Toleranslı renk eşleştirmesi ile BFS flood fill
}
```

## Güvenlik

- İzin gerektirmez (kamera, internet yok MVP'de)
- Veri sadece cihazda kalır
