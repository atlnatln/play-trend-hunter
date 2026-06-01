# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> 
> **Token tasarrufu:** Bu dosya kısa tutulur. Tarihçe → session log'ları. Detaylı teknik bilgi → SKILL.md. Strateji kararları → ROADMAP.md.

---

## 🎯 Durum

**Faz 0 aktif.** Gün 2 tamamlandı. İkinci snapshot alındı, ilk detect çalıştı.
- Snapshots: **2 adet** (2026-05-31, 2026-06-01) — 7050 app pozisyonu her biri
- Detect: **337 alert** (threshold 20.0, kalibre edildi)
- Threshold: **20.0** (önceki: 5.0, histogram analizi sonrası)
- DB: Temiz, test/mock verisi yok

## ⏭️ Sıradaki Görev

1. **İlginç app'lerin detayını çek** — Top 5-10 alert'i incele
2. **True positive analizi** — Alert'ler gerçekten anlamlı mı?
3. **3-4 gün daha veri biriktir** — Günlük `run.py full`

Detaylı fazlar → `ROADMAP.md`

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor (Google verisi) | Düşük |

Çözülen: ~~S1~~ datetime deprecated fixlendi. ~~S3~~ CacheGuard naive datetime fixlendi. ~~S4~~ Hardcoded threshold fixlendi.

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Teknik detay (API, schema, formüller, SQL) | `.kimi/skills/play-trend-hunter/SKILL.md` |
| Strateji, fazlar, ADR'lar | `ROADMAP.md` |
| Tarihçe, session detayları | `.kimi/logs/` |
| Kalıcı dersler, troubleshooting | ACE `playbook-python-ops` Ders 020-022 |

---

## 📝 Oturum Sonu Checklist

- [ ] CONTEXT.md güncelle
- [ ] Session log yaz
- [ ] Git commit
