# AGENTS.md — Play Trend Hunter

> **Rol:** Davranış kuralları, okuma sırası, oturum protokolü.
> **Ne içermez:** Teknik detay (→ SKILL.md), durum/görev (→ CONTEXT.md), tarihçe (→ session log'ları).
> **⚠️ Uzunluk:** Bu dosya system prompt'a otomatik eklenir. Sadece kalıcı kurallar; değişken bilgiler CONTEXT.md'ye.

---

## 📖 Okuma Sırası (Her Session)

1. **.kimi/CONTEXT.md** — Durum, sıradaki görev, aktif sorunlar.
2. **AGENTS.md** — Kurallar (bu dosya).
3. **SKILL.md** — Teknik referans (görev gerektiriyorsa).

**Sadece detay gerekiyorsa:** CHANGELOG.md, session log'ları, kod tabanı.

---

## 🚫 Token Tasarrufu — Katı Kurallar

> **Her `ReadFile`, `Shell`, `Glob` çağrısı ~500-2000 token harcar.**

| Durum | Ne Yapılır | Ne Yapılmaz |
|-------|-----------|-------------|
| Kullanıcı "bugün ne var / görevler" derse | Sadece `CONTEXT.md` oku, cevap ver | ROADMAP, CHANGELOG, session log, detect log parse etme |
| CONTEXT.md'de cevap varsa | Cevap ver, bitir | Ek veri çekme, DB sorgusu yapma, log parse etme |
| "Detaylı analiz" isterse | Session log + detect log oku | Glob ile 1000 dosya listeleme |
| Kod değişikliği gerekiyorsa | SKILL.md oku, ilgili dosyayı aç | Tüm modülü baştan okuma |

**Skill'de cevap varken kod tabanını kazma.**

---

## 🔄 Çalışma Döngüsü

1. **İstihbarat** — CONTEXT.md + aktif görevi bilerek başla.
2. **Veri İncelemesi** — `run.py report` veya `run.py alerts` ile CLI'dan gör. Elle DB sorgusu yapma.
3. **Keşif** — Yeni trend sinyali varsa detay çek, review analiz et.
4. **Kod Değişikliği** — Scraper, detector veya reporter'da değişiklik yap.
5. **Test** — `run.py scan` veya `run.py detect` ile doğrula.
6. **Döngü** — Başka kategori/app var mı?

---

## ✏️ Dokümantasyon Kuralı

Her değişiklik sonrası **üç** kaydı güncelle:

| Kayıt | Ne Yazılır | Dosya |
|-------|-----------|-------|
| **Durum** | Görev durumu, yeni kararlar, bug'lar | `CONTEXT.md` |
| **Tarihçe** | Detaylı yapılanlar, bulgular, karar gerekçeleri | `.kimi/logs/YYYY-MM-DD-HHMM-session.md` |
| **Teknik Referans** | Kalıcı bilgi değiştiyse | `SKILL.md` |

**Tekrar yasak:** Aynı keşfi/hatayı iki kez yapma. Öğrendiğini yaz.

---

## 🛠️ Araç Kullanımı

| Araç | Kural |
|------|-------|
| **Scraper** | Rate limiting zorunlu. Cache TTL = `config.CACHE_TTL_HOURS` (20s). Aynı kategori 24 saatte bir çekilir. |
| **Detector** | Karşılaştırma yapmadan önce en az 2 snapshot olmalı. Threshold `config.SURGE_THRESHOLD` (30.0). |
| **Detail fetch** | Tek app, tek request. Review sentiment analizi yapılabilir. |
| **SQLite** | Schema ve SQL template'ler SKILL.md §3'te. Elle sorgu yazma, modelleri kullan. |
| **Maestro** | YAML test'ler `android-template/maestro/` ve `apps/<name>/maestro/` altında. Emulator: `Pixel_6_API_34`. |
| **VLM** | `qwen2.5vl:7b` (Ollama). Smoke test sonrası, assertion hatasında, crash sonrası ekran analizi. |
| **AI Asset** | `run.py ai-assets <app> <cat>` (FLUX.1-schnell). Detaylar `flux-asset-generation` skill'inde. Üretim öncesi (Faz 1+) kullanılır. Faz 0'da `run.py assets` (PIL) yeterlidir. |

---

## 🔧 Kod Değişikliği Kuralları

- **Scraper:** `MIN_DELAY`/`MAX_DELAY` asla kaldırılmaz. Proxy eklenebilir.
- **Detector:** Threshold/formül değişikliğinde wiki'ye not et. Sadece veriye dayalı sinyal.
- **Reporter:** `__doc__` string'i güncelle. Mevcut CLI output değiştirilemez.
- **Android:** Yeni app = `cp -r android-template apps/<name>`. `namespace`, `applicationId`, `app_name` değiştir. Build hemen doğrula (`./gradlew assembleDebug`).
- **Maestro:** Her app'te `launch.yaml` zorunlu. Build → `adb install -r` → `maestro test maestro/` pipeline her değişiklikte tekrarlanır.
- **Signing:** Release için `keystore.jks` + `local.properties`. `.gitignore`'da var. Keystore mathlock-play'den kopyalanabilir.

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. AGENTS.md oku | 2. Session log yaz |
| 3. Skill oku (görev gerektiriyorsa) | 3. Skill güncelle (değişiklik varsa) |
| 4. Kullanıcıdan talimat al | 4. `run.py detect` çalıştır (veri değiştiyse) |
| | 5. Git status kontrol et |
