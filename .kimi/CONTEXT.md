# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> 
> **Token tasarrufu:** Bu dosya kısa tutulur. Tarihçe → session log'ları. Detaylı teknik bilgi → SKILL.md. Strateji kararları → ROADMAP.md.

---

## 🎯 Durum

**Faz 0 aktif.** Gün 3 tamamlandı. Üçüncü snapshot alındı, detect çalıştı, top 5 detay çekildi.
- Snapshots: **3 adet** (2026-05-31, 2026-06-01, 2026-06-02) — 7050 app pozisyonu her biri
- Detect: **449 alert** (threshold 20.0) — Gün 3'te 112 yeni alert
- Threshold: **20.0** (kalibre edildi, değişmedi)
- DB: Temiz, test/mock verisi yok

## 📋 Strateji Kararları (2026-06-02 — Kullanıcı + Agent Tartışması Sonucu)

| # | Karar | Eski Durum | Yeni Durum | Gerekçe |
|---|-------|-----------|-----------|---------|
| 1 | **Altyapı** | Flutter MVP | Kotlin Native Android | Mevcut mathlock-play pipeline'ı (Gradle, Keystore, Play Console, deploy.sh) hazır. APK boyutu küçük, Play Store performansı en iyi |
| 2 | **Test stratejisi** | Belirsiz | Maestro YAML (agent) + Manuel (sen) | Agent Maestro test'leri yazıp çalıştırabilir, assertion sonuçlarını analiz edebilir. Görsel/animasyon/oyun testleri için kullanıcı manuel test eder |
| 3 | **Web app politikası** | — | Google Play'den gelen adaylar native clone'lanacak | Web wrapper (Capacitor/PWA) Play Store'da "low quality" etiketi riski. Aday web tabanlı olsa bile native Kotlin versiyonu yapılacak |
| 4 | **Agent yetenek sınırları** | — | Metin-tabanlı model | Agent VLM (Vision-Language Model) değil. Screenshot'tan "bu renk kötü" veya "animasyon donuyor" analizi yapamaz. Araştırma: Maestro, claude-in-mobile, Mobile-Agent-E gibi araçlar var ama görsel zeka VLM (GPT-4o/Claude) gerektirir |
| 5 | **"Video gibi oyunlar" testi** | — | Maestro flow test + manuel | Akademik çözüm: Keyframe extraction (FFmpeg) + VLM (GPT-4o) analizi. Pratikte: Maestro ile level geçiş/skore assertion test'i + kullanıcı manuel oynayarak test |
| 6 | **Gerekli kurulumlar** | — | Maestro CLI + Android Emulator | Java 21 ✅ | ADB ✅ | FFmpeg ✅ | Maestro ❌ | Emulator ❌ |

## ⏭️ Sıradaki Görev

1. **Maestro + Android Emulator kurulumu** | ~20 dk
2. **mathlock-play'den "clean template" çıkarma** | ~30 dk
3. **İlk MVP app'i başlatma** — Aday app: Total Washout (oyun) veya IQ Masters (utility)
4. **2-3 gün daha veri biriktir** — Günlük `run.py full`
5. **Haftalık true positive analizi** — 3 snapshot üzerinden trend doğrulama

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

Çözülen: ~~S1~~ datetime deprecated fixlendi. ~~S3~~ CacheGuard naive datetime fixlendi. ~~S4~~ Hardcoded threshold fixlendi. ~~S5~~ Review `content` boş gelme → `google-play-scraper` v10 API alan adları (`text`, `id`, `thumbsUp`, `version`, `date`) ile düzeltildi. 350 boş review temizlendi.

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Teknik detay (API, schema, formüller, SQL) | `.kimi/skills/play-trend-hunter/SKILL.md` |
| Strateji, fazlar, ADR'lar | `ROADMAP.md` |
| Tarihçe, session detayları | `.kimi/logs/` |
| Kalıcı dersler, troubleshooting | ACE `playbook-python-ops` Ders 020-022 |

---

## 📝 Oturum Sonu Checklist

- [x] CONTEXT.md güncelle
- [x] Session log yaz (`2026-06-02-2054-session.md`)
- [x] SKILL.md güncelle (+281 satır, 12 bölüm)
- [x] CHANGELOG.md güncellendi
- [x] Git commit (5 adet)
- [x] ACE Ders 007 + 008 eklendi
- [x] Wiki ingest + lint (9/10 pass)
- [x] Maestro + Emulator kurulumu ve testi
- [x] Strateji kararları loglandı
