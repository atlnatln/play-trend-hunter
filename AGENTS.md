# AGENTS.md — Play Trend Hunter

> **Bu dosyanın rolü:** Nasıl çalışmalıyım? Davranış kuralları, okuma sırası, oturum protokolü.
> **Ne içermez:** Teknik detay (→ SKILL.md), durum/görev (→ CONTEXT.md), tarihçe (→ session log'ları).
> **⚠️ Önemli:** Bu dosya Kimi CLI tarafından **system prompt'a otomatik eklenir**. Uzun olursa token israfı olur. Sadece kalıcı davranış kuralları yazılır; değişken bilgiler .kimi/CONTEXT.md'ye.

---

## 📖 Okuma Sırası (Her Session Başında)

1. **.kimi/CONTEXT.md** — İlk oku. Durum, sıradaki görev, aktif sorunlar.
2. **AGENTS.md** — Kurallar ve protokol (bu dosya).
3. **.kimi/CHANGELOG.md** — Son değişiklikler ve gerekçeleri. "Neden 20?" sorusuna cevap burada.
4. **SKILL.md** — Teknik referans (Play Store scraping, trend detection, SQLite schema).
5. **Session log'ları** — Son 3 oturum (sadece detay gerekiyorsa).
6. **Kod tabanı** — Yukarıdakiler yeterli olmadığında.

**Token israfı yasak:** Skill'de cevap varken kod tabanını kazmak yasak. Bulduğun bilgiyi skill'e yaz (pay it forward).

---

## 🔄 Çalışma Döngüsü

1. **İstihbarat** — CONTEXT.md + aktif görevi bilerek başla.
2. **Veri İncelemesi** — SQLite DB, snapshot'lar, alert'leri kontrol et.
3. **Keşif** — Yeni trend sinyali varsa detay çek, review analiz et.
4. **Kod Değişikliği** — Scraper, detector veya reporter'da değişiklik yap.
5. **Test** — `run.py scan` veya `run.py detect` ile doğrula.
6. **Döngü** — Başka kategori/app var mı?

---

## ✏️ Dokümantasyon Kuralı

Her değişiklik sonrası **üç** kaydı güncelle:

| Kayıt | Ne Yazılır | Dosya |
|-------|-----------|-------|
| **Durum** | Görev durumu, yeni kararlar, yeni bug'lar | `CONTEXT.md` |
| **Tarihçe** | Detaylı yapılanlar, bulgular, karar gerekçeleri | `.kimi/logs/YYYY-MM-DD-HHMM-session.md` |
| **Teknik Referans** | Kalıcı bilgi değiştiyse (scraping API, detector algoritması) | `SKILL.md` |

**Tekrar yasak:** Aynı keşfi, hatayı, çözümü iki kez yapma. Öğrendiğini yaz.

---

## 🛠️ Araç Kullanımı

| Araç | Ne Zaman | Kural |
|------|----------|-------|
| **Scraper** | Yeni veri çekme gerektiğinde | Rate limiting zorunlu. Aynı kategori 24 saatte bir çekilir (cache). |
| **Detector** | `run.py detect` çalıştırıldığında | Karşılaştırma yapmadan önce en az 2 snapshot olmalı. |
| **Detail fetch** | Surge alert'i incelenirken | Tek app, tek request. Review sentiment analizi yapılabilir. |
| **SQLite** | Veri sorgulama | `.kimi/skills/play-trend-hunter/SKILL.md` §3'te schema var. |
| **Wiki** | Cross-project bağlantı, strateji kararları | `wiki/projects/play-store-trend-hunter.md` |

---

## 🔧 Kod Değişikliği Kuralları

### Scraper Katmanı

- **Node.js `gplay_fetch.js`**: Yeni method eklerken JSON output formatını bozma. Python tarafı parse eder.
- **Python `play_store.py`**: Rate limiting (`MIN_DELAY`, `MAX_DELAY`) asla kaldırılmaz. Proxy desteği eklenebilir.
- **Cache**: `CacheGuard` TTL'si `config.CACHE_TTL_HOURS`'dan alır. Günlük tarama için 24 saat standart.

### Detector Katmanı

- **Surge Score Algoritması**: `detector/surge.py` değiştirilirken threshold (`SURGE_THRESHOLD`) ve puan formülleri wiki'ye not edilmeli.
- **Yeni sinyal ekleme**: Sadece veriye dayalı sinyaller (social buzz, keyword rank vb.). Spekülatif sinyal yok.

### Reporter Katmanı

- **CLI output**: `reporter/cli.py` veya `run.py`'de değişiklik yaparken `__doc__` string'i güncellenmeli.
- **Alert formatı**: JSON/CSV export eklenebilir. Mevcut CLI output değiştirilemez (backward compat).

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. AGENTS.md oku (bu dosya) | 2. Session log yaz |
| 3. Skill oku (gerekirse) | 3. Skill güncelle (değişiklik varsa) |
| 4. Son 3 log'a göz at (gerekirse) | 4. `run.py detect` çalıştır (veri değiştiyse) |
| 5. Kullanıcıdan talimat al | 5. Git status kontrol et |
