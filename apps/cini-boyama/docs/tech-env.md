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

## Deploy Modeli

- Local debug build: `./gradlew assembleDebug`
- Release: `./gradlew assembleRelease` + keystore
- Maestro: `maestro test maestro/`

## Yasaklı Kütüphaneler

| Kütüphane | Neden Yasak | Alternatif |
|-----------|-------------|------------|
| Glide / Coil | MVP'de bitmap ihtiyacı yok, gömülü drawable yeterli | — |
| Üçüncü parti reklam SDK | MVP kapsamında reklam yok | — |

## Örnek Kod Kalıpları

```kotlin
// Flood fill algoritması
private fun floodFill(bitmap: Bitmap, x: Int, y: Int, color: Int) {
    val targetColor = bitmap.getPixel(x, y)
    if (targetColor == color) return
    // Queue-based flood fill
}
```

## Güvenlik

- İzin gerektirmez (kamera, internet yok MVP'de)
- Veri sadece cihazda kalır
