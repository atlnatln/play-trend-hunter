---
name: play-trend-hunter
description: Play Trend Hunter — Play Store trend tespiti, fast-follow stratejisi, scraping ve otomasyon
metadata:
  last_updated: 2026-05-31
  maintainer: kimi-agent
  project: play-trend-hunter
---

# Play Trend Hunter — Teknik Referans

> **Evrensel çalışma prensipleri için `AGENTS.md`.** Bu skill = kalıcı teknik referans.
> Çözülmüş sorunların tarihçesi ve kararlar → `CONTEXT.md`.

---

## 1. Proje Yapısı

```
play-trend-hunter/
├── AGENTS.md                     # Davranış kuralları (system prompt'a eklenir)
├── config.py                     # Tracked categories, collections, thresholds
├── run.py                        # CLI entry point (scan/detect/full/detail/alerts)
├── requirements.txt              # Python bağımlılıkları
├── package.json                  # Node.js bağımlılıkları (google-play-scraper)
├── .kimi/
│   ├── CONTEXT.md               # Aktif durum, görevler, sorunlar
│   ├── skills/play-trend-hunter/SKILL.md  # Bu dosya
│   └── logs/                     # Session log'ları
├── scraper/
│   ├── gplay_fetch.js           # Node.js scraper wrapper (JSON output)
│   └── play_store.py            # Python wrapper + rate limiting + caching
├── database/
│   └── models.py                # SQLite schema + CRUD
├── detector/
│   └── surge.py                 # Trend detection algoritması
└── data/
    ├── play_trend.db            # SQLite veritabanı (gitignore)
    └── .cache/                  # File cache (gitignore)
```

---

## 2. Scraping Katmanı

### Node.js `gplay_fetch.js`

`facundoolano/google-play-scraper`'ın Python portu `list()` desteklemez. Node.js orijinali kullanılır.

**Kullanım:**
```bash
node scraper/gplay_fetch.js <method> '<json_args>'
```

**Method'lar:**
| Method | Args | Output |
|--------|------|--------|
| `list` | `collection`, `category`, `num`, `fullDetail` | App listesi (rank'lı) |
| `app` | `appId`, `lang`, `country` | App detayları |
| `search` | `term`, `num`, `lang`, `country` | Arama sonuçları |
| `reviews` | `appId`, `num`, `sort`, `lang`, `country` | Review listesi |
| `categories` | — | Kategori listesi |

**Önemli:** `require('google-play-scraper').default` kullan. Direkt require artık çalışmıyor.

### Python `play_store.py`

**Rate limiting:** Her request arası 3-6 saniye rastgele bekleme.
**Caching:** `CacheGuard` ile 24 saat file cache. Aynı kategori tekrar çekilmez.

```python
from scraper.play_store import safe_fetch_list, fetch_app_detail, fetch_reviews

# Koleksiyon çek (cache'li)
apps = safe_fetch_list('TOP_FREE', 'GAME_ACTION', num=100)

# Detay çek
detail = fetch_app_detail('com.whatsapp')

# Review çek
rev_data = fetch_reviews('com.whatsapp', num=50, sort='NEWEST')
```

---

## 3. Veritabanı (SQLite)

**Schema:**

| Tablo | Amaç |
|-------|------|
| `snapshots` | Her taramanın rank listesi |
| `app_details` | App metadata (açıklama, score, install, developer vb.) |
| `reviews` | Kullanıcı review'ları |
| `surge_alerts` | Tespit edilen trend sinyalleri |

**Ana sorgular:**
```sql
-- Son 2 snapshot'ı getir (detect için)
SELECT DISTINCT snapshot_at FROM snapshots
WHERE collection = ? AND category = ?
ORDER BY snapshot_at DESC LIMIT 2;

-- Son alert'leri listele
SELECT * FROM surge_alerts WHERE dismissed = 0
ORDER BY detected_at DESC LIMIT 50;
```

**DB path:** `data/play_trend.db` (gitignore)

---

## 4. Surge Detection Algoritması

### Sinyaller ve Puan Formülleri

| Sinyal | Formül | Max Puan |
|--------|--------|----------|
| **Rank Delta** | `prev_rank - curr_rank` | ∞ (pratikte 100) |
| **Newcomer Bonus** | Listeye yeni girmişse | +15 |
| **Ratings Delta** | `delta / 100` | 50 |
| **Score Delta** | `delta * 20` | ~20 |

**Surge Score =** Rank Delta + Ratings Score + Score Score + Newcomer Bonus

**Threshold:** `SURGE_THRESHOLD = 5.0` (config.py)

### Detect Akışı

```
snapshots (current) ─┐
                     ├──→ rank_delta + newcomer + ratings + score → surge_score
snapshots (previous)─┘
                          │
                          v
                    surge_score > 5.0 ?
                          │
                    ┌─────┴─────┐
                    YES         NO
                    │            │
              save_alert()   skip
```

---

## 5. CLI Komutları

```bash
# Tüm kategorilerden son listeleri çek
python run.py scan

# Son 2 snapshot'ı karşılaştır, surge tespit et
python run.py detect

# scan + detect bir arada
python run.py full

# App detayları + son 50 review çek
python run.py detail <appId>

# Son alert'leri listele
python run.py alerts
```

---

## 6. Track Edilen Kategoriler (config.py)

**Oyunlar:** GAME_ACTION, GAME_ADVENTURE, GAME_ARCADE, GAME_PUZZLE, GAME_STRATEGY, GAME_SIMULATION, GAME_CASUAL, GAME_ROLE_PLAYING, GAME_SPORTS, GAME_RACING, GAME_BOARD, GAME_CARD, GAME_WORD, GAME_EDUCATIONAL, GAME_MUSIC, GAME_TRIVIA

**Uygulamalar:** APPLICATION, TOOLS, PRODUCTIVITY, COMMUNICATION, SOCIAL, PHOTOGRAPHY, VIDEO_PLAYERS, LIFESTYLE, HEALTH_AND_FITNESS, EDUCATION, BUSINESS, FINANCE, ENTERTAINMENT, BOOKS_AND_REFERENCE, TRAVEL_AND_LOCAL, SHOPPING, FOOD_AND_DRINK, DATING, MAPS_AND_NAVIGATION, AUTO_AND_VEHICLES, BEAUTY, ART_AND_DESIGN, EVENTS, HOUSE_AND_HOME, LIBRARIES_AND_DEMO, MEDICAL, MUSIC_AND_AUDIO, NEWS_AND_MAGAZINES, PARENTING, PERSONALIZATION, WEATHER

**Toplam:** 41 kategori × 1 koleksiyon (TOP_FREE) = 41 API call/scan

---

## 7. Troubleshooting

| Sorun | Neden | Çözüm |
|-------|-------|-------|
| `ImportError: cannot import name 'Category'` | `play-store-scraper-ng` kırık | Kullanma, Node.js scraper'ı kullan |
| `list NOT FOUND` | Python `google-play-scraper`'da `list()` yok | Normal. Node.js wrapper kullan. |
| `gplay error: ...` | Google rate limit veya layout değişikliği | Bekle ve tekrar dene. Cache sil (`rm -rf data/.cache/`) |
| `No surge alerts detected` | Tek snapshot var veya threshold yüksek | İkinci taramayı bekle veya threshold düşür (config.py) |
| `datetime.utcnow() deprecated` | Python 3.12+ | Düşük öncelik, `datetime.now(datetime.UTC)` ile değiştir |
| `installs`/`ratings` boş | Google verisi eksik | Normal, bazı app'lerde gizli. Diğer sinyallere güven. |

---

## 8. Geliştirme Notları

- **Yeni scraper methodu:** `gplay_fetch.js`'e ekle, JSON output ver. Python tarafı `play_store.py`'de `_run()` ile çağır.
- **Yeni detector sinyali:** `detector/surge.py`'de `signals` dict'ine ekle, `surge_score` formülüne kat.
- **Yeni CLI komutu:** `run.py`'de `cmd_<name>()` fonksiyonu ekle, `main()`'de `elif` bloğu ekle.
- **Yeni kategori:** `config.py` `TRACKED_CATEGORIES`'e ekle. Bir sonraki `scan`'de otomatik çekilir.
