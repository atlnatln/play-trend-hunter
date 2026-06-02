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

## ⏭️ Sıradaki Görev

1. **2-3 gün daha veri biriktir** — Günlük `run.py full`
2. **Haftalık true positive analizi** — 3 snapshot üzerinden trend doğrulama
3. **Aday app seçimi** — Fast-follow'a en uygun sinyal (YTV Player Pro ve IQ Masters öne çıkıyor)

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
- [x] Session log yaz
- [x] SKILL.md güncelle
- [x] CHANGELOG.md oluştur
- [x] AGENTS.md okuma sırasına CHANGELOG eklendi
- [x] Git commit
