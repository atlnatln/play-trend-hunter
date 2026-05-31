# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).
> 
> **Token tasarrufu:** Bu dosya kısa tutulur. Tarihçe → session log'ları. Detaylı teknik bilgi → SKILL.md. Strateji kararları → ROADMAP.md.

---

## 🎯 Durum

**Faz 0 aktif.** Gün 1 tamamlandı. İlk gerçek tarama yapıldı.
- 1. snapshot: **47 kategori, 7050 app pozisyonu, 6901 benzersiz app** (2026-05-31 ~14:30 UTC)
- Detect: Henüz çalışmadı (2. snapshot gerekli)
- Threshold: 5.0 (henüz kalibre edilmedi)
- DB: Test/mock verisi temizlendi, sıfırdan dolduruldu

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

- [x] CONTEXT.md güncelle (sadece aktif durum)
- [x] Session log yaz
- [x] Git commit
