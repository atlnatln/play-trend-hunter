---
name: play-trend-hunter
description: Play Store trend tespiti, scraping, SQLite analizi, surge detection, CLI komutları
metadata:
  last_updated: 2026-06-03
  maintainer: kimi-agent
---

# Play Trend Hunter — Teknik Referans

> Evrensel prensipler → `AGENTS.md`. Bu dosya = kalıcı teknik referans.
> Android test pipeline → `android-test-pipeline` skill. VLM screenshot → `vlm-screenshot` skill.

---

## 1. Proje Yapısı

```
play-trend-hunter/
├── config.py                     # 47 kategori, TOP_FREE, FETCH_NUM=200, threshold=20.0
├── run.py                        # CLI: scan/detect/full/detail/alerts/top-alerts/auto-detail/report
├── scraper/
│   ├── gplay_fetch.js           # Node.js wrapper (google-play-scraper)
│   └── play_store.py            # Python wrapper + rate limit (3-6s) + CacheGuard
├── database/models.py           # SQLite schema + CRUD
├── detector/surge.py            # Surge detection algoritması
├── reporter/cli.py              # CLI output formatları
├── android-template/            # Kotlin MVP template → android-test-pipeline skill
├── apps/                        # Fast-follow app'ler
└── data/
    ├── play_trend.db            # SQLite (gitignore)
    └── .cache/                  # File cache (gitignore)
```

---

## 2. Scraping Katmanı

### Node.js `gplay_fetch.js`

```bash
node scraper/gplay_fetch.js <method> '<json_args>'
```

| Method | Args |
|--------|------|
| `list` | `collection`, `category`, `num` |
| `app` | `appId`, `lang`, `country` |
| `reviews` | `appId`, `num`, `sort` |

**Önemli:** `require('google-play-scraper').default` kullan.

### Python `play_store.py`

```python
from scraper.play_store import safe_fetch_list, fetch_app_detail, fetch_reviews, CacheGuard

apps = safe_fetch_list('TOP_FREE', 'GAME_ACTION', num=200)  # cache'li
detail = fetch_app_detail('com.whatsapp')
rev_data = fetch_reviews('com.whatsapp', num=50, sort='NEWEST')
```

**Rate limit:** Her request arası 3–6 saniye rastgele bekleme.  
**Cache:** `CacheGuard` 24 saat file cache. Cache bypass: `rm -f .cache/*.json`.

---

## 3. Veritabanı (SQLite)

| Tablo | Amaç |
|-------|------|
| `snapshots` | Her taramanın rank listesi |
| `app_details` | App metadata |
| `reviews` | Kullanıcı review'ları |
| `surge_alerts` | Tespit edilen trend sinyalleri |

**Analiz SQL Template'leri:**

```sql
-- Top 20 alert (title join'li)
SELECT a.app_id, a.category, a.surge_score, a.signals,
       (SELECT title FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as title,
       (SELECT rank_position FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as rank
FROM surge_alerts a ORDER BY a.surge_score DESC LIMIT 20;

-- Score histogram
SELECT CASE 
  WHEN surge_score BETWEEN 5 AND 10 THEN '5-10'
  WHEN surge_score BETWEEN 10 AND 20 THEN '10-20'
  WHEN surge_score BETWEEN 20 AND 50 THEN '20-50'
  WHEN surge_score BETWEEN 50 AND 100 THEN '50-100'
  ELSE '100+'
END as range, COUNT(*) as cnt
FROM surge_alerts GROUP BY range;

-- Newcomer sayısı
SELECT COUNT(*) FROM surge_alerts WHERE signals LIKE '%newcomer%';

-- Yeni app'ler
SELECT app_id, title, genre, released FROM app_details
WHERE released LIKE '2026-%' OR released LIKE '2025-%'
ORDER BY released DESC;
```

**DB path:** `data/play_trend.db`

---

## 4. Surge Detection Algoritması

| Sinyal | Formül | Max Puan |
|--------|--------|----------|
| **Rank Delta** | `prev_rank - curr_rank` | ∞ |
| **Newcomer Bonus** | Listeye yeni girmişse | +15 |
| **Ratings Delta** | `delta / 100` | 50 |
| **Score Delta** | `delta * 20` | ~20 |

**Surge Score =** Rank Delta + Ratings Score + Score Score + Newcomer Bonus  
**Threshold:** `SURGE_THRESHOLD = 20.0`

*Önceki değer 5.0'dı. Histogram analizi: 5-10 aralığında 605 gürültü, 20+ aralığında 358 anlamlı alert.*

**surge.py kodu (kısaltılmış):**

```python
def detect_surges(current_rows, previous_rows, collection, category):
    current = {r["app_id"]: r for r in current_rows}
    previous = {r["app_id"]: r for r in previous_rows}
    alerts = []
    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)
        if not prev:
            signals["newcomer"] = {"current_rank": curr["rank"]}
            rank_delta_score = max(0, 50 - curr["rank"])
        else:
            rank_delta = prev["rank"] - curr["rank"]
            signals["rank_delta"] = {"previous": prev["rank"], "current": curr["rank"], "delta": rank_delta}
            rank_delta_score = max(0, rank_delta)
        ratings_score = 0
        if prev and curr.get("ratings") and prev.get("ratings"):
            ratings_delta = curr["ratings"] - prev["ratings"]
            if ratings_delta > 0:
                signals["ratings_delta"] = {"previous": prev["ratings"], "current": curr["ratings"], "delta": ratings_delta}
            ratings_score = min(ratings_delta / 100, 50)
        score_score = 0
        if prev and curr.get("score") and prev.get("score"):
            score_delta = curr["score"] - prev["score"]
            if score_delta > 0:
                signals["score_delta"] = {"previous": prev["score"], "current": curr["score"], "delta": round(score_delta, 3)}
            score_score = max(0, score_delta * 20)
        newcomer_bonus = 15 if "newcomer" in signals else 0
        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus
        if surge_score > config.SURGE_THRESHOLD:
            alerts.append({"app_id": app_id, "surge_score": surge_score, "signals": signals})
    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts
```

---

## 5. CLI Komutları

```bash
python run.py scan              # Tüm kategorileri çek (~3-5 dk)
python run.py detect            # Son 2 snapshot'ı karşılaştır
python run.py full              # scan + detect
python run.py detail <appId>    # App detay + 50 review
python run.py alerts            # Son alert'ler
python run.py top-alerts [N]    # En yüksek N alert (default 10)
python run.py auto-detail [N]   # Top N alert için detay çek (default 5)
python run.py report            # Özet rapor
python run.py ai-assets "App Name" "CATEGORY"  # FLUX ile AI asset üretimi
```

> **AI asset detayları:** `flux-asset-generation` skill'ine bak. Üretim öncesi (Faz 1+) Play Store görselleri FLUX ile, Faz 0 placeholder'ları PIL ile üretilir.

---

## 6. Track Edilen Kategoriler

**Oyunlar (16):** GAME_ACTION, GAME_ADVENTURE, GAME_ARCADE, GAME_PUZZLE, GAME_STRATEGY, GAME_SIMULATION, GAME_CASUAL, GAME_ROLE_PLAYING, GAME_SPORTS, GAME_RACING, GAME_BOARD, GAME_CARD, GAME_WORD, GAME_EDUCATIONAL, GAME_MUSIC, GAME_TRIVIA

**Uygulamalar (31):** APPLICATION, TOOLS, PRODUCTIVITY, COMMUNICATION, SOCIAL, PHOTOGRAPHY, VIDEO_PLAYERS, LIFESTYLE, HEALTH_AND_FITNESS, EDUCATION, BUSINESS, FINANCE, ENTERTAINMENT, BOOKS_AND_REFERENCE, TRAVEL_AND_LOCAL, SHOPPING, FOOD_AND_DRINK, DATING, MAPS_AND_NAVIGATION, AUTO_AND_VEHICLES, BEAUTY, ART_AND_DESIGN, EVENTS, HOUSE_AND_HOME, LIBRARIES_AND_DEMO, MEDICAL, MUSIC_AND_AUDIO, NEWS_AND_MAGAZINES, PARENTING, PERSONALIZATION, WEATHER

**Toplam:** 47 kategori × 1 koleksiyon (TOP_FREE) = 47 API call/scan  
**Fetch num:** 200 app/kategori

---

## 7. Kalıcı Dersler

| Ders | Özet |
|------|------|
| Python `google-play-scraper`'da `list()` yok | Kategori koleksiyonları sadece Node.js `facundoolano/google-play-scraper` ile çekilir |
| Node.js API `.default` export | `require('google-play-scraper').default;` kullan |
| Ban koruma zorunlu | 3–6 sn rate limit + 24 saat cache olmadan tarama yapma |
| Detect için 2 snapshot gerekli | İlk `scan` sonrası `detect` çalışmaz |
| `datetime.utcnow()` deprecated | Python 3.12+ için `datetime.now(timezone.utc)` kullan |
| Hardcoded threshold | `surge.py`'de `config.SURGE_THRESHOLD` import et |
| CacheGuard naive datetime | `datetime.fromtimestamp(mtime)` offset-naive üretiyor. `tz=timezone.utc` ekle |
| Threshold 5→20 kalibrasyonu | 150 app'lik listede +6 rank = score 6. 2024 gürültü alert. 20+ = makul |

---

## 8. Troubleshooting

| Sorun | Çözüm |
|-------|-------|
| `gplay error: ...` | Google rate limit veya layout değişikliği. Cache sil, bekle, tekrar dene. |
| `No surge alerts detected` | Tek snapshot var veya threshold yüksek. İkinci taramayı bekle. |
| `installs`/`ratings` boş | Google verisi eksik. Normal, diğer sinyallere güven. |
| Review `content` NULL | v10 API: `content`→`text`, `reviewId`→`id`. Alan adlarını güncelle. |

---

## 9. Fast-Follow Aday App Profilleme

### auto-detail Çıktısı

`run.py auto-detail 5` ile çekilen metadata:
- title, score, ratings, installs, released, genre, developer, IAP, adSupported
- 50 adet son review (NEWEST)

### Şikayet Analizi Şablonu

| App | #1 Şikayet | #2 Şikayet | Fast-Follow Fırsatı |
|-----|-----------|-----------|---------------------|
| YTV Player Pro | Çok reklam/bildirim | Review bombing | Daha az reklamlı alternatif |
| IQ Masters | Çok reklam | Abonelik pahalı ($8/hafta) | Daha ucuz, az reklamlı |
| Total Washout | Tutorial yok | Kafa karıştırıcı UI | İyi onboarding = fark |
| Timpy Cooking | Çok reklam (çocuk app'inde!) | Ücretli versiyonda bile reklam | "Reklamsız çocuk oyunu" |
| LineLeap | Ticket/email gönderilmiyor | App çöküyor | Güvenilir bilet app'i |

### Newcomer Tespiti

`released` alanına bak. Nisan 2026 ve sonrası = çok yeni app.

```sql
SELECT app_id, title, genre, released FROM app_details
WHERE released LIKE '2026-%' OR released LIKE '2025-%'
ORDER BY released DESC;
```

---

## 10. AI Asset Generation

FLUX.1-schnell tabanlı Play Store görselleri. Tam teknik referans `flux-asset-generation` skill'indedir.

```bash
python run.py ai-assets "Digital Compass" "MAPS_AND_NAVIGATION"
```

**Çıktılar:**
- `assets/output/<slug>/<slug>_ai_icon_1024.png` — 1024×1024 Play Store icon
- `assets/output/<slug>/<slug>_ai_feature_1024x500.png` — 1024×500 feature graphic

**Kritik kurallar:**
- `transformers>=5.0` ile `diffusers 0.38` uyumsuzdur; `<5.0` kullan.
- T5 tokenizer için `protobuf` ve `sentencepiece` zorunlu.
- 12GB VRAM'da `enable_sequential_cpu_offload()` + `float16` kullan.
- FLUX metin render etmede kötüdür; metin sonradan `assets/ai_postprocess.py` ile PIL overlay olarak eklenir.

## 11. Geliştirme Notları

- **Yeni scraper methodu:** `gplay_fetch.js`'e ekle, JSON output ver.
- **Yeni detector sinyali:** `detector/surge.py`'de `signals` dict'ine ekle.
- **Yeni CLI komutu:** `run.py`'de `cmd_<name>()`, `main()`'de `elif` bloğu ekle.
- **Yeni kategori:** `config.py` `TRACKED_CATEGORIES`'e ekle.
- **Yeni AI asset pipeline'ı:** `flux-asset-generation` skill'ini güncelle, `AGENTS.md`'deki Araç Kullanımı tablosuna ekle.
