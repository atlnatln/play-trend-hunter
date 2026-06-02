---
name: play-trend-hunter
description: Play Trend Hunter — Play Store trend tespiti, fast-follow stratejisi, scraping ve otomasyon
metadata:
  last_updated: 2026-06-02
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

**Analiz SQL Template'leri:**
```sql
-- Top 20 alert (title join'li)
SELECT a.app_id, a.category, a.surge_score, a.signals,
       (SELECT title FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as title,
       (SELECT rank_position FROM snapshots WHERE app_id=a.app_id ORDER BY snapshot_at DESC LIMIT 1) as rank
FROM surge_alerts a ORDER BY a.surge_score DESC LIMIT 20;

-- Score histogram (threshold kalibrasyonu için)
SELECT 
  CASE 
    WHEN surge_score BETWEEN 5 AND 10 THEN '5-10'
    WHEN surge_score BETWEEN 10 AND 15 THEN '10-15'
    WHEN surge_score BETWEEN 15 AND 20 THEN '15-20'
    WHEN surge_score BETWEEN 20 AND 30 THEN '20-30'
    WHEN surge_score BETWEEN 30 AND 50 THEN '30-50'
    WHEN surge_score BETWEEN 50 AND 100 THEN '50-100'
    ELSE '100+'
  END as range,
  COUNT(*) as cnt
FROM surge_alerts GROUP BY range;

-- Newcomer sayısı
SELECT COUNT(*) FROM surge_alerts WHERE signals LIKE '%newcomer%';

-- Kategori dağılımı
SELECT category, COUNT(*) as cnt FROM surge_alerts 
GROUP BY category ORDER BY cnt DESC LIMIT 10;
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

**Threshold:** `SURGE_THRESHOLD = 20.0` (config.py)  
*Not: Önceki değer 5.0'dı. 150 app'lik listede +6 rank bile score 6 üretiyordu, 2024 gürültü alert oluşuyordu. Histogram analizi sonrası 20 seçildi.*

### Detect Akışı

```
snapshots (current) ─┐
                     ├──→ rank_delta + newcomer + ratings + score → surge_score
snapshots (previous)─┘
                          │
                          v
              surge_score > config.SURGE_THRESHOLD ?
                          │
                    ┌─────┴─────┐
                    YES         NO
                    │            │
              save_alert()   skip
```

### surge.py Tam Kodu

```python
def detect_surges(current_rows, previous_rows, collection, category):
    current = parse_snapshot(current_rows)
    previous = parse_snapshot(previous_rows)
    alerts = []
    for app_id, curr in current.items():
        signals = {}
        prev = previous.get(app_id)
        if not prev:
            signals["newcomer"] = {"current_rank": curr["rank"], "note": "Entered top list"}
            rank_delta_score = max(0, 50 - curr["rank"])
        else:
            rank_delta = prev["rank"] - curr["rank"]  # Positive = moved up
            signals["rank_delta"] = {"previous": prev["rank"], "current": curr["rank"], "delta": rank_delta}
            rank_delta_score = max(0, rank_delta)
        # Ratings growth
        ratings_score = 0
        if prev and curr["ratings"] and prev["ratings"]:
            ratings_delta = curr["ratings"] - prev["ratings"]
            if ratings_delta > 0:
                signals["ratings_delta"] = {"previous": prev["ratings"], "current": curr["ratings"], "delta": ratings_delta}
            ratings_score = min(ratings_delta / 100, 50)
        # Score improvement
        score_score = 0
        if prev and curr["score"] and prev["score"]:
            score_delta = curr["score"] - prev["score"]
            if score_delta > 0:
                signals["score_delta"] = {"previous": prev["score"], "current": curr["score"], "delta": round(score_delta, 3)}
            score_score = max(0, score_delta * 20)
        newcomer_bonus = 15 if "newcomer" in signals else 0
        surge_score = rank_delta_score + ratings_score + score_score + newcomer_bonus
        if surge_score > config.SURGE_THRESHOLD:  # DO NOT hardcode; read from config
            alerts.append({...})
    alerts.sort(key=lambda x: x["surge_score"], reverse=True)
    return alerts
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

**Toplam:** 47 kategori × 1 koleksiyon (TOP_FREE) = 47 API call/scan
**Fetch num:** 200 app/kategori (API hard limit: 200)

---

## 7. Kalıcı Dersler (Tekrarlanmaması Gereken Hatalar)

| Ders | Kaynak | Özet |
|------|--------|------|
| Python `google-play-scraper`'da `list()` yok | Day 1 test | Kategori koleksiyonları sadece Node.js `facundoolano/google-play-scraper` ile çekilir |
| `play-store-scraper-ng` kırık | Day 1 test | RankoR'un Python portu `ImportError` veriyor, kullanılamaz |
| Node.js API `.default` export | Day 1 debug | `require('google-play-scraper').default;` kullan |
| Ban koruma zorunlu | Day 1 design | 3–6 sn rate limit + 24 saat cache olmadan tarama yapma |
| Detect için 2 snapshot gerekli | Day 1 test | İlk `scan` sonrası `detect` çalışmaz, veri birikmesi lazım |
| `datetime.utcnow()` deprecated | Day 1 refactor | Python 3.12+ için `datetime.now(timezone.utc)` kullan |
| `print_report` detector'da olmamalı | Day 1 refactor | Separation of concerns: detector = algoritma; reporter = çıktı |
| API hard limit 200 app | Day 1 test | `num > 200` request etse de max 200 döner |
| **Hardcoded threshold** | Day 2 detect | `surge.py` satır 89'da `> 5` hardcoded'dı. `config.SURGE_THRESHOLD` import edilmeli |
| **CacheGuard naive datetime** | Day 2 scan | `datetime.fromtimestamp(mtime)` offset-naive üretiyor. `tz=timezone.utc` ekle |
| **Threshold 5→20 kalibrasyonu** | Day 2 detect | 150 app'lik listede +6 rank = score 6. 2024 gürültü alert oluştu. Histogram: 20+ = 337 alert (makul) |

---

## 8. Troubleshooting

| Sorun | Neden | Çözüm |
|-------|-------|-------|
| `ImportError: cannot import name 'Category'` | `play-store-scraper-ng` kırık | Kullanma, Node.js scraper'ı kullan |
| `list NOT FOUND` | Python `google-play-scraper`'da `list()` yok | Normal. Node.js wrapper kullan. |
| `gplay error: ...` | Google rate limit veya layout değişikliği | Bekle ve tekrar dene. Cache sil (`rm -rf data/.cache/`) |
| `No surge alerts detected` | Tek snapshot var veya threshold yüksek | İkinci taramayı bekle veya threshold düşür (config.py) |
| `datetime.utcnow() deprecated` | Python 3.12+ | Düşük öncelik, `datetime.now(datetime.UTC)` ile değiştir |
| `installs`/`ratings` boş | Google verisi eksik | Normal, bazı app'lerde gizli. Diğer sinyallere güven. |
| Review `content` NULL | google-play-scraper v10 API değişikliği | `content`→`text`, `reviewId`→`id`. SKILL.md Bölüm 2'ye bak |

---

## 9. Mobil Test Altyapısı (Maestro + Android Emulator)

### 9.1 Maestro Kurulumu ve Kullanımı

```bash
# Kurulum
curl -fsSL "https://get.maestro.mobile.dev" | bash
export PATH="$PATH:$HOME/.maestro/bin"

# Versiyon kontrol
maestro --version   # 2.6.0+
```

**Temel Komutlar:**
```bash
maestro test flow.yaml              # Tek flow çalıştır
maestro test flows/                 # Tüm flow'ları çalıştır
maestro test -c flow.yaml           # Watch mode (dosya değişiminde yeniden çalıştır)
maestro hierarchy                   # Cihaz UI hiyerarşisi (element inspection)
maestro record flow.yaml            # Video kaydı
maestro download-samples            # Örnek app ve flow'lar
```

**Basit Flow Örneği:**
```yaml
appId: com.example.myapp
---
- launchApp
- tapOn: "Start Game"
- assertVisible: "Level 1"
- inputText: "Player1"
- tapOn: "Submit"
- assertVisible: "Score: 0"
```

### 9.2 Android Emulator Yönetimi

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$HOME/.maestro/bin"

# Mevcut AVD'leri listele
emulator -list-avds

# AVD başlat (headless, arka planda)
emulator -avd tablet_7inch -no-window -no-audio -gpu swiftshader_indirect &

# Cihaz bağlı mı kontrol et
adb devices

# APK yükle
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Logcat izle
adb logcat -s com.example.myapp:D
```

**Mevcut AVD'ler (Bu Makinede):**
| AVD | Boyut | API | Durum |
|-----|-------|-----|-------|
| `tablet_7inch` | 1200x1920 | 34 | ✅ Mevcut |
| `tablet_10inch` | — | 34 | ✅ Mevcut |

**Telefon AVD'si oluşturma (gerekirse):**
```bash
sdkmanager "system-images;android-34;google_apis_playstore;x86_64"
avdmanager create avd -n pixel6 -d pixel_6 -k "system-images;android-34;google_apis_playstore:x86_64"
```

### 9.3 Maestro Best Practices ve İleri Komutlar

**Visibility Assertions:**
```yaml
# Regex match (case-insensitive)
- assertVisible:
    text: ".*error.*"

# Element yoksa PASS (optional)
- assertVisible:
    text: "Tooltip"
    optional: true

# Element görünmemeli
- assertNotVisible: "Loading..."

# Relative selector (belirli bir elementin altında/üstünde)
- assertVisible:
    text: "Price: $9.99"
    below:
      text: "Sauce Labs Backpack"
```

**Repeat / Loop:**
```yaml
# JavaScript condition ile while loop
- evalScript: ${output.count = 0}
- repeat:
    while:
      true: ${output.count < 3}
    commands:
      - tapOn:
          id: "fabAddIcon"
      - evalScript: ${output.count = output.count + 1}
```

**Environment Variables:**
```yaml
appId: com.example.myapp
---
- launchApp
- tapOn: ${USERNAME}   # maestro test -e USERNAME=alice flow.yaml
```

**CI Integration:**
```bash
# JUnit XML raporu
maestro test --format junit --output results.xml flows/

# Tag filtering
maestro test --include-tags smoke --exclude-tags slow flows/

# Paralel çalıştırma (4 cihaz)
maestro test --shard-split 4 flows/
```

### 9.4 Test Stratejisi — Agent vs Kullanıcı

| Test Türü | Kim Yapar? | Araç | Neden? |
|-----------|-----------|------|--------|
| **Unit test** | Agent | JUnit (Kotlin) | Kod doğruluğu |
| **Smoke test** (app açılıyor mu?) | Agent | Maestro YAML | Otomasyon |
| **Flow test** (login → oyna → skor) | Agent | Maestro YAML | Regression |
| **Assertion/log analizi** | Agent | Maestro output + logcat | Metin tabanlı |
| **Animasyon/oyun mekaniği** | **Kullanıcı** | Manuel oynama | Agent VLM değil, görsel analiz yapamaz |
| **Renk/UI estetiği** | **Kullanıcı** | Manuel gözlem | Agent renk/aydınlatma yorumu yapamaz |
| **Crash/bug analizi** | Agent | Logcat + Maestro log | Metin tabanlı |

**Önemli:** Agent metin-tabanlı LLM'dir. Screenshot'tan "bu buton yanlış yerde", "animasyon donuyor", "renk soluk" analizi **yapamaz**. Bu tür testler kullanıcıya bırakılır.

---

## 10. Kotlin Android Build Pipeline

### 10.1 Mevcut Pipeline (mathlock-play'den kopyalanabilir)

```bash
cd projects/mathlock-play
./gradlew assembleDebug      # Debug APK (~10 sn - 1 dk)
./gradlew assembleRelease    # Release APK (keystore gerekir)
```

**Gerekli ortam değişkenleri:**
```bash
export ANDROID_HOME="$HOME/Android/Sdk"
```

**local.properties:**
```properties
sdk.dir=/home/akn/Android/Sdk
```

### 10.2 APK Yükleme ve Test Döngüsü

```bash
# 1. Build
./gradlew assembleDebug

# 2. Yükle
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 3. Maestro test
maestro test flows/smoke.yaml

# 4. Log kontrolü (crash var mı?)
adb logcat -d | grep AndroidRuntime
```

### 10.3 Play Store Release Pipeline (mathlock-play'den)

```bash
# Keystore ile release build
./gradlew bundleRelease

# Play Store internal track upload (deploy.sh)
bash deploy.sh --track internal
```

> **Not:** Play Trend Hunter app'lerinde aynı pipeline kullanılacak. mathlock-play'in `deploy.sh`, `keystore.jks`, `play-console.json` dosyaları template olarak kopyalanabilir.

---

## 12. Kimi CLI Entegrasyonu (Agent İçin)

### 12.1 Agent Yetenekleri ve Sınırları

**Agent yapabilir:**
- Kod yazar, dosya oluşturur/siler (`WriteFile`, `StrReplaceFile`)
- Shell komutları çalıştırır (`Shell`) — Gradle build, ADB, Maestro
- Web'de araştırma yapar (`SearchWeb`, `FetchURL`)
- Context7 dokümantasyonu sorgular (`query-docs`)
- Wiki ingest/lint yapar (`wiki-assistant.py`)
- ACE dersleri yönetir (`ace-curator.py`)
- Sub-agent spawn eder (`Agent` tool)
- Playwright ile web testi yapar (sadece web app'lerde)

**Agent yapamaz:**
- Görsel analiz (screenshot'tan UI element tespiti, renk yorumu, animasyon değerlendirmesi)
- Video/animasyon anlama (oyun mekaniği, particle effect, fizik motoru)
- Elle cihazda oynama (gesture hızı, dokunsal feedback)
- Gerçek zamanlı oyun testi (frame-by-frame analiz)

**Sonuç:** Agent test araçlarını (Maestro YAML) yazar ve çalıştırır. Assertion sonuçlarını ve log'ları analiz eder. Ama "bu oyun eğlenceli mi?" veya "animasyon akıcı mı?" gibi görsel/somut testleri kullanıcı yapar.

### 12.2 Bu Projedeki Kimi CLI Kullanımı

```bash
# Session başlat (proje dizininden)
cd /home/akn/local/projects/play-trend-hunter && kimi

# Agent'a özel prompt örnekleri:
# "run.py full çalıştır"
# "top 10 alert'i analiz et"
# "Maestro smoke test yaz ve çalıştır"
# "YTV Player Pro için detay çek"
```

**Config:** `~/.kimi/config.toml` (global) ve `play-trend-hunter/.kimi/` (proje seviyesi)

**Skills:**
- Proje seviyesi: `play-trend-hunter/.kimi/skills/play-trend-hunter/SKILL.md` (bu dosya)
- Kullanıcı seviyesi: `~/.kimi/skills/`

**MCP:**
- Context7 (zaten bağlı): `kimi mcp list`
- Maestro MCP (opsiyonel): `maestro mcp` çalıştırarak kurulabilir

### 12.3 Background Tasks

Uzun süren işlemler (Gradle build, Maestro test, run.py full) arka planda çalıştırılır:
```bash
# Agent arka planda başlatır, tamamlandığında bildirim gelir
./gradlew assembleDebug          # ~30-60 sn
python run.py full               # ~3-5 dk (47 kategori)
maestro test flows/smoke.yaml    # ~10-30 sn
```

---

## 11. Fast-Follow Aday App Profilleme

### 11.1 auto-detail Çıktısı Analizi

`run.py auto-detail 5` komutu şunları çeker:
1. App metadata (title, score, ratings, installs, released, genre)
2. 50 adet son review (1-2★ odaklı şikayet analizi için)

### 11.2 Şikayet Analizi Şablonu

| App | #1 Şikayet | #2 Şikayet | Fast-Follow Fırsatı |
|-----|-----------|-----------|---------------------|
| YTV Player Pro | Çok fazla reklam/bildirim | Review bombing | Daha az reklamlı alternatif |
| IQ Masters | Çok fazla reklam | Abonelik çok pahalı ($8/hafta) | Daha ucuz, az reklamlı |
| Total Washout | Tutorial yok | Kafa karıştırıcı UI | İyi onboarding = fark |
| Timpy Cooking | Çok fazla reklam (çocuk app'inde!) | Ücretli versiyonda bile reklam | "Reklamsız çocuk oyunu" |
| LineLeap | Ticket/email gönderilmiyor | App çöküyor | Güvenilir bilet app'i |

### 11.3 Newcomer Tespiti

`released` alanına bak. Nisan 2026 ve sonrası = çok yeni app. Erken sinyal ama riskli (henüz kanıtlanmamış).

```sql
-- Yeni app'leri bul
SELECT app_id, title, genre, released FROM app_details
WHERE released LIKE '2026-%' OR released LIKE '2025-%'
ORDER BY released DESC;
```

---

## 8. Geliştirme Notları

- **Yeni scraper methodu:** `gplay_fetch.js`'e ekle, JSON output ver. Python tarafı `play_store.py`'de `_run()` ile çağır.
- **Yeni detector sinyali:** `detector/surge.py`'de `signals` dict'ine ekle, `surge_score` formülüne kat.
- **Yeni CLI komutu:** `run.py`'de `cmd_<name>()` fonksiyonu ekle, `main()`'de `elif` bloğu ekle.
- **Yeni kategori:** `config.py` `TRACKED_CATEGORIES`'e ekle. Bir sonraki `scan`'de otomatik çekilir.
