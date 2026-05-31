# Play Trend Hunter — Aktif Context

> **Kural:** Session başında ilk okunan dosya. AGENTS.md (kurallar) → bu dosya (durum) → SKILL.md (teknik referans, gerekirse).

---

## 🎯 Durum

**Gün 1 tamamlandı.** MVP çalışıyor, veri kalitesi doğrulandı, strateji belirlendi.

- Scraper: Node.js `google-play-scraper` + Python wrapper ✅
- Database: SQLite ✅
- Detector: Rank delta + newcomer + ratings + score delta ✅
- CLI: `scan`, `detect`, `full`, `detail <appId>`, `alerts` ✅
- Altyapı: AGENTS.md, CONTEXT.md, SKILL.md, `.kimi/` dizini ✅
- Ayrı repo: `main` branch, ilk commit ✅
- ROADMAP.md: Stratejik yol haritası yazıldı ✅

**Aktif Faz:** Faz 0 — Veri Birikimi ve Kalibrasyon (Hafta 1–2)

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

## ⏭️ Sonraki Adımlar (ROADMAP.md'ye detaylı bak)

**Faz 0: Veri Birikimi ve Kalibrasyon (Hafta 1–2)**
1. Günlük `run.py full` çalıştır — 7–14 gün veri biriktir
2. False positive/negative analizi yap — threshold ayarla
3. İlk "ilginç" sinyalleri yakala — 3–5 aday app listesi oluştur

**Faz 1: İlk Fast-Follow (Hafta 3 – Ay 1 Sonu)**
4. En güçlü sinyali seç → reverse engineer → şikayet listesi
5. Flutter MVP geliştir (3–7 gün)
6. Soft launch + ASO

**Faz 2–3: Otomasyon ve Ölçek (Ay 2–3)**
7. Telegram alert botu
8. Review sentiment analizi
9. VPS cron kurulumu
10. 3 app portfolyo hedefi

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
