# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> **Token tasarrufu:** Bu dosyada cevap varsa ek veri çekme.

---

## ⏭️ Bugünün Görevleri

1. **Gün 6 snapshot** — `run.py full` (Faz 0 devam)
2. **Algo karşılaştırması** — 5 gün veri birikmiş, hangisi daha iyi aday yakalıyor?
3. **Aday app'leri emulator'de aç** — Aurora Store → Digital Compass, Love Island, Borrow Cash, IQ Masters
4. **İlk fast-follow app değerlendir** — Aday seç, reverse engineering yap

---

## 🎯 Durum

**Faz 0 aktif.** Gün 6 tamamlandı.
- Snapshots: **8 adet** (2026-05-31 → 06-05) — ~9.400 app/gün
- **Recent Delta:** 174 alert | **Persistence:** 196 alert | **WMA:** 77 | **Slope:** 49
- Threshold: **40.0** (30'dan yükseltildi) | Cache TTL: **20 saat**
- Android altyapısı: Template ✅, Emulator ✅, Maestro ✅
- AI Asset Generator: 🚫 Kaldırıldı. `assets/ai_generator.py`, `assets/ai_postprocess.py`, `assets/generator.py` ve `flux-asset-generation` skill `uygulama-gelistir-play`'e taşındı. `run.py ai-assets` ve `run.py assets` komutları silindi.
- İlk fast-follow app: Henüz başlatılmadı

### 🏆 Gün 5 — Top 5 Sinyal (Her İkisinde de)
| # | App | Skor | Kategori |
|---|-----|------|----------|
| 1 | Digital Compass | 99 | MAPS |
| 2 | NBC LA: News | 82 | NEWS |
| 3 | Love Island USA | 70 | ENTERTAINMENT |
| 4 | Borrow Cash | 68 | FINANCE |
| 5 | Happy Dentist | 67 | GAME_EDUCATIONAL |

**Sadece Persistence:** IQ Masters (30), YTV Player Pro (30), McAlister's Deli (56.3)

---

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor | Düşük |
| S7 | Büyük marka gürültüsü (Waze, Facebook Lite) | Düşük |

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
