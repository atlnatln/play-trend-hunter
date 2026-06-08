# Digital Compass — MVP Planı

> Fast-follow hedefi: `com.compass.digital.direction.directionfinder.pro`
> Seçim gerekçesi: Rank 195 → 53 → 39 → 38 (3 günde +157 sıçrama). Basit utility, mevcut app kalitesiz.

---

## 🎯 Farklar (Better Clone)

| Sorun | Orijinal App (1-2★ Review'lar) | Bizim Çözümümüz |
|-------|-------------------------------|-----------------|
| **#1 Reklam bombardımanı** | "nothing but ads", "can't use compass due to ads" | **ZERO reklam** |
| **#2 Yanlış yön** | "pointed north said west" | Low-pass filter + stabilizasyon |
| **#3 Gereksiz izinler** | "access to photos suspicious" | **Sadece sensör** (runtime izin gerektirmez) |
| **#4 Çıkış zorluğu** | "Can't get out of the app" | Standart Android back tuşu |
| **#5 Karmaşık UI** | "not user friendly" | Minimal tek ekran |

---

## 📱 Feature Set (v1.0.0 MVP)

### Core
- [x] Pusula (SensorManager: accelerometer + magnetometer)
- [x] Derece gösterimi (0-360°)
- [x] Yön adı (N, NE, E, SE, S, SW, W, NW)
- [x] Portrait lock
- [x] Dark theme (Material Design 3)

### Fark Yaratan
- [x] **ZERO reklam** (en büyük fark)
- [x] **ZERO gereksiz izin** (sadece sensör, hiçbir izin istemez)
- [x] Doğru çalışan yön (low-pass filter, 100ms update interval)
- [x] Minimal APK boyutu (~5.7MB debug)

### V1.1+ (Sonra)
- [ ] Kalibrasyon uyarısı (8-figür)
- [ ] GPS koordinatları (opsiyonel)
- [ ] Altitude / basınç (barometer varsa)
- [ ] Widget
- [ ] AdMob (opsiyonel, kullanıcı tercihli)

---

## 🎨 UI Wireframe

```
┌─────────────────────────────┐
│  [Status Bar — purple_700]  │
├─────────────────────────────┤
│                             │
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
   [Navigation Bar — black]
```

**Renkler:**
- Arka plan: `#1A0033` (purple_900)
- Derece: `#FFFFFF` (white)
- Yön: `#03DAC5` (teal_200)
- İpucu: `#FFFFFF` @ 70% alpha

---

## 📝 ASO Stratejisi

### Title Önerileri
1. `Digital Compass — Accurate & No Ads` ⭐ (Önerilen)
2. `Simple Compass: Accurate, Ad-Free`
3. `Digital Compass Pro — Minimal & Fast`

### Short Description
> "Accurate digital compass with zero ads. No permissions needed. Just open and use."

### Keywords
`compass, digital compass, magnetic compass, navigation, direction, heading, no ads compass, free compass, accurate compass, simple compass`

### Farkı Vurgula (Play Store Listing)
- 🚫 **No ads** — No interruptions, no banners
- 🔒 **No permissions** — No location, no photos, no network
- ⚡ **Instant** — Opens in under 1 second
- 🎯 **Accurate** — Calibrated sensor fusion

---

## 🏗️ Teknik Kararlar

| Konu | Karar |
|------|-------|
| Dil | Kotlin |
| Min SDK | 26 (Android 8.0) |
| Target SDK | 35 |
| Architecture | Tek Activity, ViewBinding |
| Sensors | TYPE_ACCELEROMETER + TYPE_MAGNETIC_FIELD |
| Update rate | 100ms throttling (SENSOR_DELAY_UI) |
| Filter | SensorManager.getRotationMatrix (native) |
| Theme | Material3 Dark NoActionBar |
| APK boyutu hedefi | < 5MB (release, R8 + shrinkResources) |

---

## ✅ Build Durumu

```
./gradlew assembleDebug  → BUILD SUCCESSFUL in 22s
APK: app/build/outputs/apk/debug/app-debug.apk (5.7MB)
```

---

## 📅 Sonraki Adımlar

1. **Signing** — `keystore.jks` oluştur (mathlock-play'den kopyala)
2. **Release build** — `./gradlew assembleRelease`
3. **APK boyut optimizasyonu** — `isMinifyEnabled = true`, `shrinkResources = true`
4. **Play Console** — Yeni app oluştur, internal testing
5. **Maestro test** — Emulator'de launch + assertion (emulator kurulunca)
6. **Icon/Feature Graphic** — `flux-asset-generation` skill'i ile üret

---

> **MVP Süresi Tahmini:** 1 gün (kod zaten yazıldı, sadece polish + ASO + build)
> **Soft Launch:** Internal + Closed testing (3-7 gün)
