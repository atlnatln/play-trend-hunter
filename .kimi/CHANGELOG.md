# Play Trend Hunter — Değişiklik ve Bakım Logu

> **Amaç:** Her kod/config değişikliğinin neden yapıldığı. Bir sonraki agent'ın otomatik olarak okuduğu context.
> **Format:** Tarih | Dosya | Değişiklik | Gerekçe (neden, hangi veriye dayalı)
> **Okuma:** Her session başında AGENTS.md → CONTEXT.md → BU DOSYA

---

## 2026-06-01 — Gün 2: İlk Detect & Altyapı Güçlendirme

| # | Dosya | Değişiklik | Gerekçe |
|---|-------|-----------|---------|
| 1 | `scraper/play_store.py` | `CacheGuard.get`: `datetime.fromtimestamp(mtime, tz=timezone.utc)` | Offset-naive/aware karşılaştırması `TypeError` fırlatıyordu. Tüm 47 kategori başarısız, 0 app kaydedildi. [ACE Ders 020] |
| 2 | `detector/surge.py` | `import config` eklendi, `if surge_score > config.SURGE_THRESHOLD:` | Hardcoded `> 5` satır 89'daydı. `config.py` değiştirilmesine rağmen detect eski değeri kullanıyordu. 2024 yanlış alert üretildi. [ACE Ders 021] |
| 3 | `config.py` | `SURGE_THRESHOLD = 20.0` (önceki: 5.0) | Histogram analizi: score 5-10 aralığında 605 gürültü, 10-15'te 352, 15-20'de 709 alert. 20+ aralığında 358 anlamlı alert kaldı. 1.5 günlük snapshot aralığı için 20 makul elbow noktası. [ACE Ders 022] |
| 4 | `run.py` | `top-alerts [N]`, `auto-detail [N]`, `report` komutları eklendi | Günlük/haftalık veri analizini hızlandırmak. `top-alerts` ile en güçlü sinyaller 1 komutla görülüyor. `auto-detail` ile manuel `detail <appId>` yerine otomatik detay çekim. `report` ile snapshot/alert/kategori özet. |
| 5 | `.kimi/skills/play-trend-hunter/SKILL.md` | surge.py tam kodu, SQL template'leri, 3 yeni ders | Kodu tekrar okumak zorunda kalmamak için self-contained referans. SQL'leri baştan yazmamak için template. [Token tasarrufu altyapısı] |
| 6 | `wiki/ace/playbook-python-ops.md` | ACE Ders 020, 021, 022 eklendi | Aynı hataların tekrarlanmasını önlemek. Cross-session, cross-project öğrenme. |
| 7 | `.kimi/CONTEXT.md` | 48 satır → 24 satır, delta-only yapı | Her session'da okunan satır sayısını azaltmak. Tarihçe session log'lara, teknik detay SKILL.md'ye taşındı. |
| 8 | `database/models.py` | `get_top_alerts()`, `get_alert_count_by_category()`, `get_snapshot_dates()` | `top-alerts` ve `report` komutları için veri erişim katmanı. title ve rank JOIN'li sorgu. |
| 9 | `reporter/cli.py` | `print_top_alerts()`, `print_report()` genişletme | Score sıralı alert gösterimi. Signals JSON parse desteği. |
| 10 | `config.py` | `FETCH_NUM = 200` (önceki: 150) | Daha fazla app pozisyonu = daha iyi newcomer tespiti. Alt sıralar (150-200) volatil ama erken sinyal kaynağı. API hard limit 200, request sayısı aynı (47 kategori), sadece response büyüyor. |
| 11 | `scraper/gplay_fetch.js` | `Math.min(num, 200)` (önceki: 150) | config.py ile senkronize. JavaScript tarafında da 200 limiti. |

### Bugünkü Bulgular (Detect Sonuçları)
- **337 alert** (threshold 20 ile)
- **En güçlü sinyal:** YTV Player Pro (VIDEO_PLAYERS): score 137, rank #142→#5
- **Pattern:** VPN/Tunnel app'leri yoğun (TOOLS), Video chat yükselişte (SOCIAL), Spor canlı skor patlamış (EVENTS/NEWS)
- **Newcomer oranı:** %2 — çoğu app zaten listedeydi, rank yükseldi
- **Giren/Çıkan:** 519 app girdi, 519 app çıktı (47 kategori toplamı)

---

## 2026-06-02 — Gün 3: Üçüncü Snapshot, Aday App Profilleme, Review Bug Fix

| # | Dosya | Değişiklik | Gerekçe |
|---|-------|-----------|---------|
| 1 | `data/play_trend_hunter.db` | Silindi (boş dosya) | Kafa karışıklığı yaratıyordu. Gerçek DB `play_trend.db`. |
| 2 | `run.py full` | Günlük scan + detect çalıştırıldı | Faz 0 veri birikimi. 3. snapshot oluşturuldu. |
| 3 | `run.py auto-detail 5` | Top 5 alert için detay + review çekildi | True positive analizi için app metadata ve kullanıcı şikayetleri toplandı. |
| 4 | `.kimi/CONTEXT.md` | Gün 3 durumu, top 5 sinyal tablosu, sıradaki görevler | Agent context'i güncel kalmalı. |
| 5 | `database/models.py` | `save_reviews`: alan adları `google-play-scraper` v10 API'ye uygun hale getirildi | `reviewId→id`, `content→text`, `thumbsUpCount→thumbsUp`, `reviewCreatedVersion→version`, `at→date`. 350 boş review temizlendi. |

### Bugünkü Bulgular (Gün 3 Detect Sonuçları)
- **112 yeni alert** (threshold 20 ile, toplam 449)
- **En güçlü sinyal:** YTV Player Pro (VIDEO_PLAYERS): score 137, rank #142→#5 (3 gün)
- **Yeni app:** Total Washout: Surf Arcade (Nisan 2026, 10K+ install, 4.68★) — fast-follow adayı
- **Pattern:** Video player'lar, eğitim oyunları ve event app'leri yoğun

### 📝 1-2★ Review Şikayet Analizi (Top 5)
| App | #1 Şikayet | #2 Şikayet |
|-----|-----------|-----------|
| YTV Player Pro | Çok fazla reklam/bildirim | Review bombing (1★'lar anlamsız) |
| IQ Masters | Çok fazla reklam | Abonelik çok pahalı ($8/hafta) |
| Total Washout | Tutorial/talimat yok | Kafa karıştırıcı UI |
| Timpy Cooking | Çok fazla reklam (çocuk app'inde!) | Ücretli versiyonda bile reklam var |
| LineLeap | Ticket/email gönderilmiyor | App çöküyor/açılmıyor |

---

## 2026-06-02 — Strateji Tartışması & Kararlar (Agent + Kullanıcı)

**Bağlam:** Kullanıcı "hangi altyapıyla uygulama yaratalım?" sorusunu gündeme getirdi. Agent internet araştırması yaptı, mevcut yetkinlikleri analiz etti.

### Kararlar

| # | Karar | Açıklama |
|---|-------|----------|
| 1 | **Altyapı: Kotlin Native Android** | Flutter iptal. Mevcut mathlock-play pipeline'ı (Gradle, Keystore, Play Console JSON, deploy.sh) doğrudan kullanılabilir. Dart öğrenme eğrisi + yeni pipeline = 2-3 gün kayıp. |
| 2 | **Test: Maestro YAML + Manuel** | Agent Maestro test'leri yazıp shell'den çalıştırabilir, assertion sonuçlarını analiz edebilir. Görsel/animasyon/oyun mekaniği testleri kullanıcı tarafından manuel yapılacak. |
| 3 | **Web app: Yapılmayacak** | Google Play'den gelen aday app'ler native Kotlin clone'lanacak. Capacitor/PWA/Trusted Web Activity "low quality" etiketi riski taşır. |
| 4 | **Agent yetenek sınırları** | Agent metin-tabanlı model (VLM değil). Screenshot'tan "bu renk kötü", "animasyon donuyor" analizi yapamaz. Araştırma: VideoGameQA-Bench, GlitchBench, Mobile-Agent-E, claude-in-mobile, Maestro MCP gibi araçlar mevcut ama hepsi VLM (GPT-4o/Claude) gerektirir. |
| 5 | **"Video gibi oyunlar" testi** | Statik tek screenshot yetersiz (akademik F1: 0.46). Çözüm: Keyframe extraction (FFmpeg) + VLM analizi. Pratikte: Maestro flow test (level geçiş, skor assertion) + kullanıcı manuel oyun testi. |

### Araştırma Bulguları
- **Maestro MCP:** Maestro CLI içinde built-in MCP server var. `maestro mcp` komutu ile başlatılır. AI agent emulator'de app launch, tap, swipe, screenshot, view hierarchy inspection yapabilir.
- **claude-in-mobile:** Rust binary (2MB). ADB üzerinden Android kontrolü. Annotated screenshot + UI tree + tap/swipe/type. MCP server olarak çalışır.
- **Mobile-Agent-E / DroidRun / AutoDroid:** ADB + screenshot + LLM ile Android navigasyonu. Akademik/araştırma projeleri.
- **Vision-Language Models (GPT-4o):** Gameplay video'larından bug frame extraction F1: 0.79. Ama agent'ın kendi modeli VLM değil.

### Mevcut Ortam Durumu
| Araç | Durum |
|------|-------|
| Java 21 | ✅ |
| ADB | ✅ |
| FFmpeg | ✅ |
| Maestro | ❌ (kurulum gerekli) |
| Android Emulator | ❌ (kurulum gerekli) |

---

## 2026-06-02 — Android Altyapı Kurulumu: AVD, Maestro, Clean Template, Dizin Yapısı

| # | Dosya | Değişiklik | Gerekçe |
|---|-------|-----------|---------|
| 1 | `android/` → `android-template/` | Mevcut `android/` dizini yeniden adlandırıldı | Çoklu app yapısı için template ve instance ayrımı. Her yeni app `apps/<name>/` altında `cp -r android-template` ile oluşturulacak |
| 2 | `apps/` | Yeni dizin oluşturuldu | Fast-follow app'lerin merkezi konumu. Şu an boş, ilk app buraya gelecek |
| 3 | `maestro-lib/` | Yeni dizin oluşturuldu | Paylaşılan Maestro test snippet'leri. Tekrar kullanılabilir flow'lar (login, onboarding, purchase vb.) |
| 4 | `android-template/` | Clean Kotlin MVP template oluşturuldu | mathlock-play'den sadeleştirilmiş. Sadece `core-ktx`, `appcompat`, `material`, `constraintlayout`. Billing, Chart, ACRA, Biometric, Security-Crypto çıkarıldı. ViewBinding açık |
| 5 | `android-template/maestro/launch.yaml` | İlk Maestro E2E testi yazıldı | `launchApp` + `assertVisible` ile app açılış doğrulaması. Pixel 6 AVD'de çalıştırıldı, `COMPLETED` |
| 6 | `Pixel_6_API_34.avd` | AVD oluşturuldu | Cihaz: Pixel 6, API 34 (Android 14), 1080×2400, 420 dpi, `google_apis/x86_64`. Daha gerçekçi test ortamı |
| 7 | `~/.maestro/bin/maestro` | Maestro v2.6.0 kuruldu | Agent'ın yazabildiği, shell'den çalıştırabildiği UI test framework'ü. YAML formatı |
| 8 | `AGENTS.md` | Android Katmanı + Maestro/Emulator/ADB araç kuralları eklendi | Sonraki agent'ların test pipeline'ını, app oluşturma akışını, Maestro kullanımını bilmesi için |

### Android Pipeline Doğrulama
```bash
# Tüm adımlar başarıyla tamamlandı:
cd android-template && ./gradlew assembleDebug     # BUILD SUCCESSFUL (11s)
adb install -r app/build/outputs/apk/debug/app-debug.apk   # Success
maestro test maestro/launch.yaml                    # 2 assertion COMPLETED
```

---

## Değişiklik Ekleme Kuralı

Her kod/config değişikliğinde buraya satır ekle:

```markdown
| # | `dosya.py` | Kısa değişiklik özeti | Neden yapıldı? Hangi veri/hata/sonuç dayandı? |
```

**Zorunlu alanlar:**
1. **Hangi dosya** — En az 1 dosya adı
2. **Ne değişti** — 1 cümle
3. **Neden** — Veriye dayalı gerekçe. "Tahmin ettim" yazılmaz. "X hatası aldık, Y sonuç gördük" yazılır.

**İsteğe bağlı:** ACE Ders referansı (eğer kalıcı ders çıktıysa)
