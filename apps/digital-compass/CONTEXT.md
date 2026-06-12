# Digital Compass — Devam Context

> Bu dosya yeni bir Kimi session'ında devam etmek için hazırlanmıştır.
> Son güncelleme: 2026-06-09

## Proje Yapısı

```
projects/play-trend-hunter/apps/digital-compass/
├── app/src/main/java/com/akn/digitalcompass/
│   ├── MainActivity.kt          ← GPS + sensör + UI + kalibrasyon
│   ├── CompassView.kt           ← Custom Canvas View (2D/3D pusula + bubble level)
│   ├── CompassTheme.kt          ← FLAT / CLASSIC_3D enum
│   └── CompassThemeManager.kt   ← SharedPreferences ile tema kaydetme
├── app/src/main/res/layout/activity_main.xml
├── app/src/main/res/values/strings.xml
├── app/src/main/res/values/colors.xml
├── app/src/main/res/drawable/bg_info_panel.xml  ← YENİ: yuvarlak köşeli panel arka planı
├── app/src/main/res/drawable/calibrate_figure8.xml
├── app/src/main/res/drawable/calibrate_progress.xml
└── app/src/main/AndroidManifest.xml
```

## Son Yapılan Değişiklikler

### 1. ✅ Info Panel Görünürlük Sorunu ÇÖZÜLDÜ (2026-06-09)
**Sorun:** `MaterialCardView` + `MaterialSwitch` kombinasyonu telefonda/emülatörde render olmuyordu.
**Çözüm:**
- `MaterialCardView` → basit `LinearLayout` + `@drawable/bg_info_panel` (yuvarlak köşeli shape)
- `MaterialSwitch` → `androidx.appcompat.widget.SwitchCompat`
- `compass_view`: `layout_height="360dp"` → `0dp` + `layout_weight="1"` (dinamik boyutlanma)
- Ana `LinearLayout` içindeki redundant `spacer` (weight=1) kaldırıldı — `compass_view` zaten weight=1 ile boşluğu kaplıyor

**Sonuç:** Info Panel hem telefonda hem emülatörde görünüyor.

### 2. 3D Tema Sistemi
- `CompassTheme` enum: `FLAT` (teal/mor flat) ve `CLASSIC_3D` (altın/bronz 3D)
- `CompassThemeManager` SharedPreferences ile seçimi kalıcı tutar
- Sağ üstte "2D"/"3D" toggle butonu

### 3. Custom CompassView (Canvas)
- `drawCompassFlat()` — minimal teal çember, N/E/S/W işaretleri
- `drawCompass3D()` — altın gradient kenar, koyu iç yüz, cam highlight, altın kapak
- `drawNeedleFlat()` / `drawNeedle3D()` — iki renkli iğne (N kırmızı, S beyaz)
- `drawBubbleInsideCompass()` — **pusula içinde** hareket eden baloncuk
- `Camera` ile 3D perspective transform (rotateX/Y)
- Baloncuk 3D transform içinde çiziliyor (pusula ile aynı perspective'de)

### 4. Su Terazisi (Bubble Level)
- Pusula dairesinin içinde, merkeze göre offset hesaplanır
- `roll` → x, `pitch` → y, max 25° clamp
- Sınır kontrolü: daire dışına çıkmaz
- Renk: ortada yeşil, kenarda kırmızı

### 5. GPS Koordinatları
- `LocationManager` + `LocationListener`
- `ACCESS_FINE_LOCATION` izni
- Enlem/boylam `tv_coords`'ta gösterilir

### 6. Info Panel (ÇALIŞIYOR)
- `LinearLayout` + `bg_info_panel.xml` arka plan
- Satır 1: μT | Altimeter | True/Mag North Switch (`SwitchCompat`)
- Satır 2: Sensör durum dotları (Mag • Acc • GPS) — yeşil/sarı/kırmızı
- Satır 3: Calibrate butonu

### 7. Kalibrasyon Overlay
- `FrameLayout` root + `calibration_overlay` (GONE/VISIBLE)
- Figure 8 vector drawable (`calibrate_figure8.xml`) — turkuaz renkli
- Progress bar (`calibrate_progress.xml`)
- Accuracy durumu real-time güncellenir
- Buton: `btn_calibrate` → overlay aç, `btn_calibrate_done` → kapat
- **Test:** Emülatörde ve telefonda çalışıyor

### 8. True North / Magnetic North
- `GeomagneticField` ile declination hesaplanır
- `SwitchCompat` ile toggle
- `useTrueNorth` bayrağı azimuth hesaplamasına eklenir

### 9. Sensör Accuracy Tracking
- `onAccuracyChanged` → magnetometer & accelerometer accuracy
- Dot renkleri: yeşil (HIGH), sarı (MEDIUM), kırmızı (LOW)
- LOW ise sarı banner gösterilir: "Wave phone in figure-8 to calibrate"

## Build & Deploy

```bash
cd /home/akn/local/projects/play-trend-hunter/apps/digital-compass
./gradlew :app:assembleDebug
adb -s 4fd99276 install -r app/build/outputs/apk/debug/app-debug.apk
```

## Emulator
- `emulator-5554` (Pixel_6_API_34)
- Gerçek telefon: `4fd99276`

## Bağımlılıklar
- `androidx.core:core-ktx:1.12.0`
- `androidx.appcompat:appcompat:1.6.1`
- `com.google.android.material:material:1.11.0`
- `androidx.constraintlayout:constraintlayout:2.1.4`

## Notlar
- `minSdk = 26`, `targetSdk = 35`, `compileSdk = 35`
- ViewBinding aktif (`buildFeatures { viewBinding = true }`)
- `bg_info_panel.xml`: `@color/purple_700` + `corners radius="12dp"`
- `SwitchCompat` `scaleX/Y="0.65"` ile boyutlandırıldı
