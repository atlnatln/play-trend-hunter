# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> 
> **Token tasarrufu:** Bu dosya kısa tutulur. Tarihçe → session log'ları. Detaylı teknik bilgi → SKILL.md. Strateji kararları → ROADMAP.md.

---

## 🎯 Durum

**Faz 0 aktif.** Gün 3 tamamlandı. Android geliştirme altyapısı kuruldu, clean template oluşturuldu, test pipeline çalışıyor.
- Snapshots: **3 adet** (2026-05-31, 2026-06-01, 2026-06-02) — 7050 app pozisyonu her biri
- Detect: **449 alert** (threshold 20.0)
- DB: Temiz, test/mock verisi yok

### 🛠️ Android Geliştirme Altyapısı (YENİ — 2026-06-02)

| Araç | Durum | Versiyon / Detay |
|------|-------|------------------|
| **Kotlin / Gradle** | ✅ | AGP 8.2.2, Kotlin 1.9.20, compileSdk 35 |
| **Pixel 6 AVD** | ✅ | API 34, 1080×2400, 420 dpi, cold boot tamam |
| **Maestro** | ✅ | v2.6.0, PATH: `~/.maestro/bin` |
| **ADB** | ✅ | Emulator bağlı (`emulator-5554`) |
| **Clean Template** | ✅ | `android-template/` dizininde, build + test geçti |

### 📁 Dizin Yapısı (YENİ — 2026-06-02)

```
play-trend-hunter/
├── android-template/        ← Clean Kotlin MVP template
│   ├── app/                 ← namespace: com.akn.playtrendhunter
│   ├── maestro/             ← launch.yaml (E2E test)
│   └── ...
├── apps/                    ← Her fast-follow app burada
├── maestro-lib/             ← Paylaşılan Maestro snippet'leri
├── scraper/                 ← Python tarafı (root'ta kaldı)
├── detector/
├── reporter/
└── ...
```

### 🧪 Test Pipeline (Çalışıyor)

```bash
cd android-template
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
maestro test maestro/launch.yaml
```

---

## ⏭️ Sıradaki Görev

1. **İlk fast-follow app başlat** — Aday: Total Washout (GAME_ACTION, surf arcade) veya IQ Masters (EDUCATION)
2. **Günlük veri biriktirme** — `run.py full` (Faz 0 devam)
3. **Haftalık true positive analizi** — 3 snapshot üzerinden trend doğrulama
4. **Maestro test kütüphanesi** — `maestro-lib/common/` altında yeniden kullanılabilir snippet'ler

### 🏆 Gün 3'ün En Güçlü Sinyalleri
| # | App | Skor | Kategori | Durum |
|---|-----|------|----------|-------|
| 1 | YTV Player Pro | 137.0 | VIDEO_PLAYERS | #142→#5 (3 günde) |
| 2 | IQ Masters - Brain Games | 104.02 | EDUCATION | #134→#30 |
| 3 | Total Washout: Surf Arcade | 95.0 | GAME_ACTION | Yeni, Nisan 2026 |
| 4 | Timpy Cooking Games for Kids | 94.26 | GAME_EDUCATIONAL | #137→#44 |
| 5 | LineLeap | 90.0 | EVENTS | #147→#57 |

Detaylı fazlar → `ROADMAP.md`

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor (Google verisi) | Düşük |

Çözülen: ~~S1~~ datetime deprecated fixlendi. ~~S3~~ CacheGuard naive datetime fixlendi. ~~S4~~ Hardcoded threshold fixlendi. ~~S5~~ Review `content` boş gelme → v10 API alan adlarıyla düzeltildi. ~~S6~~ Maestro + Emulator kurulumu tamamlandı.

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Teknik detay (API, schema, formüller, SQL, Android template) | `.kimi/skills/play-trend-hunter/SKILL.md` |
| Android template, build, Maestro komutları | `AGENTS.md` §Araç Kullanımı, §Android Katmanı |
| Strateji, fazlar, ADR'lar | `ROADMAP.md` |
| Tarihçe, session detayları | `.kimi/logs/` |
| Kalıcı dersler, troubleshooting | ACE `playbook-python-ops` Ders 020-022 |

---

## 📝 Oturum Sonu Checklist

- [x] CONTEXT.md güncelle
- [x] Session log yaz (`2026-06-02-2055-session.md`)
- [x] CHANGELOG.md güncelle
- [x] AGENTS.md güncelle (Android + Maestro kuralları)
- [x] Git commit
