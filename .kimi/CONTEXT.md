# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> **Token tasarrufu:** Bu dosyada cevap varsa ek veri çekme.

---

## ⏭️ Bugünün Görevleri

1. **Gün 8 snapshot** — `run.py full` (Faz 0 devam)
2. **Digital Compass emulator'de aç** — Aurora Store ile yükle, reverse engineering
3. **Digital Compass MVP planı** — Feature set, UI wireframe, ASO title
4. **Android template'den fork** — `apps/digital-compass/` oluştur, build doğrula

---

## 🎯 Durum

**Faz 0 aktif.** Gün 7 tamamlandı (2026-06-07).
- Snapshots: **9 adet** (2026-05-31 → 06-07) — ~9.400 app/gün
- **Recent Delta:** 260 alert | **Persistence:** 308 alert | **WMA:** 188 | **Slope:** 152
- Threshold: **40.0** | Cache TTL: **20 saat**
- Android altyapısı: Template ✅, Emulator ✅, Maestro ✅
- İlk fast-follow app: **Digital Compass** seçildi ✅

### 🏆 Gün 7 — Top 10 Sinyal (Tüm Algoritmalar)
| # | App | Skor | Kategori | Algoritma |
|---|-----|------|----------|-----------|
| 1 | Winnser - Quiz Game | 188.33 | GAME_TRIVIA | Tümü |
| 2 | Digital Compass | 142.0 | MAPS | Persistence |
| 3 | YTV Player Pro | 137.0 | VIDEO_PLAYERS | Persistence |
| 4 | Cafe Racer | 135.01 | GAME_RACING | Recent/WMA |
| 5 | Vlad & Niki Supermarket | 134.01 | GAME_EDUCATIONAL | Recent/WMA |
| 6 | shapes.inc | 134.0 | SOCIAL | Recent/WMA |
| 7 | KSAT Plus | 132.0/198.0 | NEWS | Slope #1 |
| 8 | Grass Master | 148.05/118.05 | GAME_PUZZLE | Persistence/Recent |
| 9 | Cry Analyzer | 117.3/175.5 | PARENTING | Slope #3 |
| 10 | Arrow Path | 99.99 | GAME_CASUAL | Recent |

### 🎯 Fast-Follow Aday Değerlendirmesi
**Seçilen: Digital Compass** (`com.compass.digital.direction.directionfinder.pro`)
- **Neden:** Basit utility (tek ekran), mevcut app kalitesiz (3.76★, 182 rating), şikayetler net.
- **1-2★ şikayetler:** (1) Reklam bombardımanı — "nothing but ads", (2) Yanlış yön — "pointed north said west", (3) Gereksiz izin — "access to photos suspicious", (4) Çalışmıyor.
- **Better clone fırsatı:** Daha az reklam, doğru çalışan compass, gereksiz izin yok, temiz UI.
- **MVP süresi tahmini:** 1-2 gün (tek Activity, SensorManager).

**Reddedilen adaylar:**
- Winnser: Scam etiketi ("doesn't pay", "points disappeared"), quiz marketi doygun.
- Cafe Racer: 10M+ install, 165K rating — çok büyük rekabet, fast-follow değil.
- Grass Master: SayGames (büyük publisher), 4.86★ — zaten iyi app.
- Cry Analyzer: AI modeli gerekli, subscription billing karmaşası — MVP süresi uzun.
- Arrow Path: "Too easy, boring" — game design yeteneği gerekir.

### 📊 Algo Karşılaştırması (Gün 7)
| Algo | Alerts | Güçlü Yön | Zayıf Yön |
|------|--------|-----------|-----------|
| **Recent** | 260 | Ani viral sıçramalar (Winnser, Cafe Racer) | Gürültülü, tek gün spike'ları yakalar |
| **Persistence** | 308 | Trend sürekliliği, az kaçırma | En gürültülü, büyük marka yakalayabilir |
| **WMA** | 188 | Recent'e göre daha temiz | Aynı app'leri tekrar eder |
| **Slope** | 152 | En temiz, trend app'leri (KSAT, Cry Analyzer) | Ani sıçramaları kaçırır (Winnser yok!) |

**Karar:** Tek algoritma yerine **Persistence + Slope birleşimi** en iyi fast-follow adaylarını veriyor. Threshold 40.0 kalıcı.

---

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor | Düşük |
| S7 | Büyük marka gürültüsü (Waze, Facebook Lite) | Düşük |
| S10 | `top-alerts` çıktısı duplicate (her app 2 kez) | Düşük |

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
| Tarihçe | `.kimi/logs/` |
| Detect logları | `logs/detect_YYYY-MM-DD.json` |
