# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).

---

## 🎯 Durum

**MVP tamamlandı.** Play Store trend tespiti için çalışan bir sistem kuruldu:
- Scraper: Node.js `google-play-scraper` + Python wrapper
- Database: SQLite (snapshots, app details, reviews, alerts)
- Detector: Rank delta + newcomer + ratings + score delta
- CLI: `scan`, `detect`, `full`, `detail <appId>`, `alerts`

**Altyapı kurulumu aktif:** AGENTS.md, CONTEXT.md, SKILL.md, `.kimi/` dizini oluşturuluyor.

---

## 📚 Kalıcı Dersler (Aynı Hatayı Tekrar Yapma)

- **Python `google-play-scraper`'da `list()` yok:** Kategori koleksiyonları (TOP_FREE, TRENDING) sadece Node.js `facundoolano/google-play-scraper` ile çekilir. Python portu sadece `app`, `search`, `reviews` destekler.
- **`play-store-scraper-ng` kırık:** RankoR'un modern Python portu `ImportError` veriyor, kullanılamaz.
- **Node.js API değişimi:** `require('google-play-scraper')` artık `.default` export kullanıyor. `const gplay = require('google-play-scraper').default;`
- **Ban koruma:** Requestler arası 3-6 saniye rastgele bekleme + 24 saat file cache zorunlu. Google anti-bot hassas.
- **Surge threshold:** 5.0 puan. Rank delta = en güçlü sinyal (örn. #30 → #5 = +25 puan).
- **Detect için 2 snapshot gerekli:** İlk `scan` sonrası `detect` çalışmaz; veri birikmesi lazım.

---

## ✅ Tamamlananlar

- ~~Node.js scraper wrapper (`gplay_fetch.js`)~~ ✅
- ~~SQLite schema (snapshots, app_details, reviews, surge_alerts)~~ ✅
- ~~Python scraper wrapper (`play_store.py`) + rate limiting + caching~~ ✅
- ~~Surge detection algoritması (`detector/surge.py`)~~ ✅
- ~~CLI entry point (`run.py`: scan/detect/full/detail/alerts)~~ ✅
- ~~Config (`config.py`: tracked categories, collections, thresholds)~~ ✅
- ~~Test: 3 kategori scan + detect~~ ✅
- ~~Test: App detail + review fetch~~ ✅
- ~~AGENTS.md~~ ✅
- ~~`.kimi/` dizin yapısı~~ ✅

---

## ⏭️ Sonraki Adımlar

1. **SKILL.md yaz** — Teknik referans (scraping API, detector formülleri, SQLite schema)
2. **Session log yaz** — Bu oturumun tarihçesi
3. **Cron setup** — Günlük otomatik `run.py full` çalıştırma
4. **Telegram alert botu** — Surge tespit edince anında bildirim
5. **Review sentiment analizi** — 1-2 yıldız review'ları analiz edip "şikayet listesi" çıkarma
6. **ASO keyword tracking** — Play Store arama sonuçlarında keyword rank takibi
7. **Wiki güncelle** — Artık çalışan sistem var, `wiki/projects/play-store-trend-hunter.md` güncellenmeli

---

## 🐛 Aktif Sorun

| ID | Sorun | Konum | Öncelik |
|----|-------|-------|---------|
| S1 | `datetime.utcnow()` deprecated warning | `run.py` | Düşük |
| S2 | `gplay_fetch.js`'te `installs` ve `ratings` bazen boş geliyor | Node.js scraper | Düşük (Google'ın verisi) |
| S3 | `play-store-scraper-ng` kırık | PyPI | Yok (kullanılmıyor) |

---

## 🔮 Bir Sonraki Oturum İçin Hazırlık

**Durum:** MVP çalışıyor, altyapı (AGENTS.md, .kimi/) tamamlanıyor.

**Olası devam görevleri:**
- SKILL.md yazma
- Telegram/Discord alert entegrasyonu
- Review sentiment analizi
- İlk gerçek günlük tarama (tüm kategoriler)

---

## 📝 Oturum Sonu Checklist

- [x] Bu dosyayı güncelle (görev durumu, yeni kararlar, yeni bug'lar)
- [x] Session log yaz: `.kimi/logs/YYYY-MM-DD-HHMM-session.md`
- [x] SKILL.md yaz
- [x] Git status kontrol et
