# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> 
> **Token tasarrufu:** Bu dosya kısa tutulur. Tarihçe → session log'ları. Detaylı teknik bilgi → SKILL.md. Strateji kararları → ROADMAP.md.

---

## 🎯 Durum

**Faz 0 aktif.** Gün 1 tamamlandı. MVP çalışıyor, veri kalitesi doğrulandı.
- Scraper ✅ | Detector ✅ | CLI ✅ | Altyapı ✅ | Ayrı repo ✅
- `FETCH_NUM = 150` (test edildi, 847ms)
- Teknik borç temizlendi (datetime deprecation, reporter SoC, review unique index)

## ⏭️ Sıradaki Görev

1. **7 gün veri biriktir** — Günlük `run.py full`
2. **Threshold kalibrasyonu** — False positive/negative analizi
3. **İlk aday app'leri belirle** — 3–5 ilginç sinyal

Detaylı fazlar → `ROADMAP.md`

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| S2 | `installs`/`ratings` bazen boş geliyor (Google verisi) | Düşük |

Çözülen: ~~S1~~ `datetime.utcnow()` deprecated → `timezone.utc` ile fixlendi.

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Teknik detay (API, schema, formüller) | `.kimi/skills/play-trend-hunter/SKILL.md` |
| Strateji, fazlar, ADR'lar | `ROADMAP.md` |
| Tarihçe, session detayları | `.kimi/logs/` |
| Kalıcı dersler, troubleshooting | `SKILL.md` §6–7 |

---

## 📝 Oturum Sonu Checklist

- [ ] CONTEXT.md güncelle (sadece aktif durum)
- [ ] Session log yaz
- [ ] Git commit
