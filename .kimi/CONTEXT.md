# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> **Token tasarrufu:** Bu dosyada cevap varsa ek veri çekme.

---

## ⏭️ Bugünün Görevleri (2026-06-08)

1. ✅ **Gün 8 snapshot** — `run.py full` (Faz 0 devam)
2. ⏭️ **Digital Compass emulator'de aç** — Aurora Store ile yükle, reverse engineering (emulator yok, sonraki session)
3. ✅ **Digital Compass MVP planı** — Feature set, UI wireframe, ASO title (`apps/digital-compass/MVP.md`)
4. ✅ **Android template'den fork** — `apps/digital-compass/` oluştur, build doğrula (`BUILD SUCCESSFUL`)

---

## ⏭️ Sonraki Session Görevleri

1. **Signing + Release build** — keystore oluştur, `./gradlew assembleRelease`, APK boyut < 5MB
2. **Play Console** — Yeni app kaydı, internal testing track
3. **Icon/Feature Graphic** — `flux-asset-generation` skill'i ile asset üretimi
4. **Emulator kurulumu** — Maestro test pipeline'ı için AVD oluştur
5. **Gün 9 snapshot** — Faz 0 devam (threshold kalibrasyonu)

---

## 🎯 Durum

**Faz 0 aktif.** Gün 8 tamamlandı (2026-06-08).
- Snapshots: **10 adet** (2026-05-31 → 06-08) — ~9.400 app/gün
- **Recent:** 398 alert | **Persistence:** 457 alert | **WMA:** 154 | **Slope:** 214
- Threshold: **40.0** | Cache TTL: **20 saat**
- Android altyapısı: Template ✅, Emulator ❌ (kurulu değil), Maestro ✅
- İlk fast-follow app: **Digital Compass** — kod yazıldı, build başarılı ✅

### 🏆 Gün 8 — Top 10 Sinyal (Recent Algo)
| # | App | Skor | Kategori | Rank |
|---|-----|------|----------|------|
| 1 | Winnser - Quiz Game | 178.67 | GAME_TRIVIA | 15 |
| 2 | Cafe Racer | 149.0 | GAME_RACING | 45 |
| 3 | shapes.inc - AI with friends | 131.41 | SOCIAL | 25 |
| 4 | Real Piano For Pianists | 126.0 | GAME_MUSIC | 49 |
| 5 | ToonShort: Short Dramas/Reels | 119.43 | ENTERTAINMENT | 50 |
| 6 | Breaking News Launcher | 119.0 | NEWS_AND_MAGAZINES | 55 |
| 7 | Artisan Home Tour MN | 115.0 | EVENTS | 81 |
| 8 | AntiVirus Sweep & Security | 112.0 | TOOLS | 31 |
| 9 | Meescan | 111.0 | LIBRARIES_AND_DEMO | 83 |
| 10 | Apple TV: Shows, Movies & More | 110.0 | APPLICATION | 77 |

### 🎯 Fast-Follow: Digital Compass
**App ID:** `com.compass.digital.direction.directionfinder.pro`

**Rank geçmişi:**
| Tarih | Rank | Δ |
|-------|------|---|
| 06-04 | 195 | — |
| 06-05 | 53 | +142 |
| 06-07 | 39 | +14 |
| **06-08** | **38** | **+1 (stabilize)** |

**Momentum durumu:** Yüksek rank'ta stabilize (38). Alert üretmiyor (küçük Δ) ama hala TOP 40'da.

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
| Tarihçe | `.kimi/logs/` |
| Detect logları | `logs/detect_YYYY-MM-DD.json` |
