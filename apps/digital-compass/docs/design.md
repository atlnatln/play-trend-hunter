# Digital Compass — Onaylanmış Tasarım

> AIDLC-lite: Bu belge kod için tek doğru kaynaktır.  
> Onay tarihi: 2026-06-08  
> Versiyon: 1.0.0

---

## 1. Genel Tasarım

Tek Activity, tek ekran. Portrait lock. Dark theme (Material3).
Zero reklam. Zero gereksiz izin.

## 2. UI Layout

```
┌─────────────────────────────┐
│  [Status Bar — purple_700]  │
├─────────────────────────────┤
│                             │
│         247°                │  ← 96sp, thin, white
│                             │
│          SW                 │  ← 48sp, bold, teal_200
│                             │
│                             │
│                             │
│  Hold your device flat...   │  ← 14sp, alpha 0.7
│                             │
└─────────────────────────────┘
```

**Renkler:**
- Arka plan: `#1A0033` (purple_900)
- Derece: `#FFFFFF` (white)
- Yön: `#03DAC5` (teal_200)
- İpucu: `#FFFFFF` @ 70% alpha

## 3. Sensor Yönetimi

**Sensörler:**
- `TYPE_ACCELEROMETER` — cihaz yönü
- `TYPE_MAGNETIC_FIELD` — manyetik alan

**Update rate:** `SENSOR_DELAY_UI` + 100ms throttling

**Azimuth hesaplama:**
```
SensorManager.getRotationMatrix(rotationMatrix, null, accel, magnet)
SensorManager.getOrientation(rotationMatrix, orientationAngles)
azimuth = Math.toDegrees(orientationAngles[0])
degrees = ((azimuth + 360) % 360).toInt()
```

**Yön adı eşlemesi:**
| Derece | Yön |
|--------|-----|
| 338-22 | N |
| 23-67 | NE |
| 68-112 | E |
| 113-157 | SE |
| 158-202 | S |
| 203-247 | SW |
| 248-292 | W |
| 293-337 | NW |

## 4. Permissions

**İstenen izinler:** YOK

Sensörler runtime izin gerektirmez. `AndroidManifest.xml`'de `<uses-permission>` yok.

## 5. Build Konfigürasyonu

```kotlin
namespace = "com.akn.digitalcompass"
applicationId = "com.akn.digitalcompass"
minSdk = 26
targetSdk = 35
versionCode = 1
versionName = "1.0.0"
```

## 6. Dosya Yapısı

```
app/src/main/
├── AndroidManifest.xml
├── java/com/akn/digitalcompass/
│   └── MainActivity.kt
└── res/
    ├── layout/activity_main.xml
    ├── values/
    │   ├── strings.xml
    │   ├── colors.xml
    │   └── themes.xml
    └── drawable/
        └── ic_launcher_foreground.xml
```

## 7. Test Planı

- [x] `./gradlew assembleDebug` BUILD SUCCESSFUL (4s, 5.5MB APK)
- [ ] `./gradlew assembleRelease` BUILD SUCCESSFUL (signing sonrası)
- [x] Maestro: launch + "Hold your device flat" görünür
- [ ] Cihazı döndürünce derece değişiyor (manuel test)
- [ ] Yön adı doğru (N, NE, E...) (manuel test)

> Not: Maestro test dosyası düzeltildi — `assertVisible: "Digital Compass"` kaldırıldı çünkü tema `NoActionBar` ve başlık ekranda görünmüyor.

## 8. Değişiklik Geçmişi

| Tarih | Değişiklik | Kim |
|-------|-----------|-----|
| 2026-06-08 | v1.0.0 — İlk tasarım | Kimi |
| 2026-06-08 | v1.0.1 — Build + Maestro test PASSED, back-propagation | Kimi |
