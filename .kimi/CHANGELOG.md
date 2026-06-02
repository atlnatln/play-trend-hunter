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

## 2026-06-02 — Gün 3: Üçüncü Snapshot, Aday App Profilleme

| # | Dosya | Değişiklik | Gerekçe |
|---|-------|-----------|---------|
| 1 | `data/play_trend_hunter.db` | Silindi (boş dosya) | Kafa karışıklığı yaratıyordu. Gerçek DB `play_trend.db`. |
| 2 | `run.py full` | Günlük scan + detect çalıştırıldı | Faz 0 veri birikimi. 3. snapshot oluşturuldu. |
| 3 | `run.py auto-detail 5` | Top 5 alert için detay + review çekildi | True positive analizi için app metadata ve kullanıcı şikayetleri toplandı. |
| 4 | `.kimi/CONTEXT.md` | Gün 3 durumu, top 5 sinyal tablosu, sıradaki görevler | Agent context'i güncel kalmalı. |

### Bugünkü Bulgular (Gün 3 Detect Sonuçları)
- **112 yeni alert** (threshold 20 ile, toplam 449)
- **En güçlü sinyal:** YTV Player Pro (VIDEO_PLAYERS): score 137, rank #142→#5 (3 gün)
- **Yeni app:** Total Washout: Surf Arcade (Nisan 2026, 10K+ install, 4.68★) — fast-follow adayı
- **Pattern:** Video player'lar, eğitim oyunları ve event app'leri yoğun
- **Sorun:** Review `content` alanı scraper'dan boş geliyor (S3?) — şikayet analizi yapılamadı

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
