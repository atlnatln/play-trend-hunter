# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> **Token tasarrufu:** Bu dosyada cevap varsa ek veri çekme.

---

## ⏭️ Bugünün Görevleri (2026-06-10)

1. ✅ **Gün 10 snapshot** — `run.py full` (Faz 0 devam)
2. ✅ **Aday uygulama analizi** — Yeni sinyaller incelendi, detect logları parse edildi
3. ✅ **Çini Boyama MVP** — `apps/cini-boyama/` fork, kod, build (`BUILD SUCCESSFUL`)
4. ✅ **Çini Boyama 12 desen genişletmesi** — 1024×1024 asset'ler, erkek/kız çocuk temaları, Maestro/emulator test
5. ⏭️ **Digital Compass emulator'de aç** — Aurora Store ile yükle, reverse engineering
6. ⏭️ **Signing + Release build** — keystore oluştur, `./gradlew assembleRelease`

---

## ⏭️ Sonraki Session Görevleri

1. **Signing + Release build** — keystore oluştur, `./gradlew assembleRelease`, APK boyut < 5MB
2. **Play Console** — Yeni app kaydı, internal testing track
3. **Icon/Feature Graphic** — `flux-asset-generation` skill'i ile asset üretimi
4. **Emulator kurulumu** — Maestro test pipeline'ı için AVD oluştur
5. **Gün 11 snapshot** — Faz 0 devam (threshold kalibrasyonu)
6. **Çini Boyama polish** — Geometrik desen aşırı yoğunluğu ve Roket arka-plan boyama sorununu çöz

---

## 🎯 Durum

**Faz 0 aktif.** Gün 10 tamamlandı (2026-06-10).
- Snapshots: **12 adet** (2026-05-31 → 06-10) — ~9.300 app/gün
- **Recent:** 262 alert | **Persistence:** 316 alert | **WMA:** 81 | **Slope:** 334
- Threshold: **40.0** | Cache TTL: **20 saat**
- Android altyapısı: Template ✅, Emulator ❌ (kurulu değil), Maestro ✅
- İlk fast-follow app: **Digital Compass** — kod yazıldı, build başarılı ✅

### 🏆 Gün 10 — Top 10 Sinyal (Recent Algo)
| # | App | Skor | Kategori | Rank |
|---|-----|------|----------|------|
| 1 | Winnser - Quiz Game | 188.33 | GAME_TRIVIA | 43 |
| 2 | Winnser - Quiz Game | 178.67 | GAME_TRIVIA | 43 |
| 3 | Cafe Racer | 149.0 | GAME_RACING | 50 |
| 4 | Digital Compass for Android | 142.0 | MAPS_AND_NAVIGATION | 49 |
| 5 | YTV Player Pro | 137.0 | VIDEO_PLAYERS | 49 |
| 6 | Cafe Racer | 135.01 | GAME_RACING | 50 |
| 7 | Vlad & Niki Supermarket game | 134.01 | GAME_EDUCATIONAL | 23 |
| 8 | shapes.inc - AI with friends | 134.0 | SOCIAL | 101 |
| 9 | KSAT Plus | 132.0 | NEWS_AND_MAGAZINES | 109 |
| 10 | KSAT Plus | 132.0 | NEWS_AND_MAGAZINES | 109 |

### 🎯 Fast-Follow: Digital Compass
**App ID:** `com.compass.digital.direction.directionfinder.pro`

**Rank geçmişi:**
| Tarih | Rank | Δ |
|-------|------|---|
| 06-04 | 195 | — |
| 06-05 | 53 | +142 |
| 06-07 | 39 | +14 |
| 06-08 | 38 | +1 (stabilize) |
| **06-10** | **49** | **-11 (soğuma)** |

**Momentum durumu:** Rank #49'e düştü, alert üretmiyor. Soğuma sinyali. Fast-follow kararı: **Beklemede** — release build yapılabilir ama yeni sinyale kaynak aktarımı düşünülebilir.

**Build durumu:**
- `apps/digital-compass/` oluşturuldu (template'ten fork)
- `MainActivity.kt`: SensorManager + accelerometer + magnetometer
- UI: Dark theme, tek ekran, derece + yön adı
- `./gradlew assembleDebug` → **BUILD SUCCESSFUL in 22s**
- APK: `app-debug.apk` (5.7MB)

**MVP dokümantasyonu:** `apps/digital-compass/MVP.md`
- Feature set, UI wireframe, ASO title/keywords, teknik kararlar

**Karşılaştırma (vs Orijinal):**
| Özellik | Orijinal | Bizimki |
|---------|----------|---------|
| Reklam | Her ekranda | Yok |
| İzin | Fotoğraf/medya | Yok (sadece sensör) |
| Doğruluk | Kullanıcı şikayeti var | Low-pass filter stabilizasyon |
| Çıkış | Zor | Standart Android back |
| UI | Karmaşık | Minimal tek ekran |

### 🎨 Fast-Follow: Çini Boyama
**App ID:** `com.akn.ciniboyama`

**Durum:** MVP tamamlandı, 12 desene genişletildi (2026-06-10).

**Desen envanteri:**
| # | ID | Ad | Tema | Notlar |
|---|----|-----|------|--------|
| 1 | `iznik_mandala` | İznik Mandala | Klasik | ✅ Çalışıyor |
| 2 | `floral_tile` | Çiçekli Çini | Klasik | ✅ Çalışıyor |
| 3 | `geometric_tile` | Geometrik | Klasik | ⚠️ Çok yoğun (~297k piksel), çocuklar için zor |
| 4 | `arabesque_tile` | Arapça Motifli | Klasik | — |
| 5 | `car_tile` | Araba Çinisi | Erkek | ✅ Açılıyor, boyanıyor, progress güncelleniyor |
| 6 | `dino_mandala` | Dinozor Mandala | Erkek | — |
| 7 | `rocket_stars` | Roket ve Yıldızlar | Erkek | ⚠️ Arka plan koyu; line-art conversion'da fillable olarak görünebilir |
| 8 | `soccer_mandala` | Futbol Topu Mandala | Erkek | — |
| 9 | `butterfly_tile` | Kelebek Çinisi | Kız | — |
| 10 | `unicorn_mandala` | Unicorn Mandala | Kız | — |
| 11 | `princess_crown` | Prenses Tacı | Kız | — |
| 12 | `heart_mandala` | Kalp Mandala | Kız | — |

**Teknik kararlar:**
- Tüm asset'ler 1024×1024 PNG; `drawable-nodpi` ile otomatik scale engelleniyor.
- `ColoringView.kt`: `isLineColor = r+g+b < 180`, `isFillable = r+g+b > 600`, glaze overlay alpha = 180.
- Line-art: `FIND_EDGES` + `grey_dilation(3)` + `min_size=12`. Kritik bug fix: `labeled-1` indexing yerine `mask[labeled]` kullanıldı (arka plan label 0 doğru işleniyor).
- Progress callback artık `setPattern()` **öncesinde** atanarak `0 / N tamamlandı` doğru gösteriyor.

**Testler:**
- `./gradlew assembleDebug` → BUILD SUCCESSFUL.
- Maestro smoke test (`maestro/launch.yaml`) → PASSED.
- Emülatör (Pixel_6_API_34): `Araba Çinisi` açılıyor, tıklama ile boyama çalışıyor, progress canlı güncelleniyor.

**Bilinen sorunlar:**
- `geometric_tile` çok küçük bölgelerden oluşuyor (~297k piksel). Çocuk kullanılabilirliği için daha sade bir geometrik desenle değiştirilmeli.
- `rocket_stars` deseninin koyu gece arka planı, `isFillable` threshold'u nedeniyle ya hiç boyanmıyor ya da beklenmedik şekilde boyanıyor. Preview/line-art gözden geçirilmeli.

---

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor | Düşük |
| S7 | Büyük marka gürültüsü (Waze, Facebook Lite) | Düşük |
| S10 | `top-alerts` çıktısı duplicate (her app 2 kez) | Düşük |
| ~~S11~~ | ~~Emulator kurulu değil~~ | ~~Çözüldü — Pixel_6_API_34 çalışıyor, Maestro PASSED~~ |
| S12 | `run.py full` stdout buffer'lanıyor (background task output 0) | Düşük — `-u` flag ile çözülebilir |

Çözülen: ~~S1~~ datetime. ~~S3~~ CacheGuard. ~~S4~~ Hardcoded threshold. ~~S5~~ Review boş. ~~S6~~ Maestro/Emulator. ~~S8~~ IQ Masters kayboluyor. ~~S9~~ Cumulative delta gürültüsü.

---

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Teknik detay | `.kimi/skills/play-trend-hunter/SKILL.md` |
| Android/Maestro | `.kimi/skills/android-test-pipeline/SKILL.md` |
| VLM | `.kimi/skills/vlm-screenshot/SKILL.md` |
| AI Asset (taşındı) | `uygulama-gelistir-play/.kimi/skills/flux-asset-generation/SKILL.md` |
| Strateji/ADR'lar | `ROADMAP.md` |
| Digital Compass MVP | `apps/digital-compass/MVP.md` |
| Çini Boyama | `apps/cini-boyama/docs/design.md` |
| Çini Boyama assets | `apps/cini-boyama/tools/generate_assets.py` |
| Tarihçe | `.kimi/logs/` |
| Detect logları | `logs/detect_YYYY-MM-DD.json` |
