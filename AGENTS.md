# AGENTS.md — Play Trend Hunter

> **Rol:** Davranış kuralları, okuma sırası, oturum protokolü.
> **Ne içermez:** Teknik detay (→ SKILL.md), durum/görev (→ CONTEXT.md), tarihçe (→ session log'ları).
> **⚠️ Uzunluk:** Bu dosya system prompt'a otomatik eklenir. Sadece kalıcı kurallar; değişken bilgiler CONTEXT.md'ye.

---

## 📖 Okuma Sırası (Her Session)

### Proje Seviyesi Çalışma (Scraper, Detector, Reporter)
1. **.kimi/CONTEXT.md** — Durum, sıradaki görev, aktif sorunlar.
2. **AGENTS.md** — Kurallar (bu dosya).
3. **SKILL.md** — Teknik referans (görev gerektiriyorsa).

### App Seviyesi Çalışma (apps/<isim>/ içinde)
1. **apps/<isim>/.kimi/CONTEXT.md** — App durumu.
2. **apps/<isim>/docs/questions.md** — Cevap bekleyen sorular var mı?
3. **apps/<isim>/docs/design.md** — Onaylanmış tasarım (kod için tek kaynak).
4. **apps/<isim>/.kimi/AGENTS.md** — App-spesifik kurallar.

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
| **AI Asset** | 🚫 Kaldırıldı. Asset üretimi `uygulama-gelistir-play` altına taşındı. Bak `flux-asset-generation` skill'i (artık `uygulama-gelistir-play/.kimi/skills/` altında). |

---

## 🔧 Kod Değişikliği Kuralları

- **Scraper:** `MIN_DELAY`/`MAX_DELAY` asla kaldırılmaz. Proxy eklenebilir.
- **Detector:** Threshold/formül değişikliğinde wiki'ye not et. Sadece veriye dayalı sinyal.
- **Reporter:** `__doc__` string'i güncelle. Mevcut CLI output değiştirilemez.
- **Android:** Yeni app = `cp -r apps/_template apps/<name>`. `namespace`, `applicationId`, `app_name` değiştir. Build hemen doğrula (`./gradlew assembleDebug`). `_template` AIDLC-lite uyumludur (`.kimi/`, `docs/` hazır).
- **Maestro:** Her app'te `launch.yaml` zorunlu. Build → `adb install -r` → `maestro test maestro/` pipeline her değişiklikte tekrarlanır.
- **Signing:** Release için `keystore.jks` + `local.properties`. `.gitignore`'da var. Keystore mathlock-play'den kopyalanabilir.

---

## 🏭 App Factory (App Seviyesi Çalışma)

Her app (`apps/<isim>/`) kendi `.kimi/` context'iyle bağımsız çalışır.

### Hiyerarşi

```
play-trend-hunter/
├── .kimi/              → Proje seviyesi (trend detection, scraper)
└── apps/
    ├── <app-a>/
    │   ├── .kimi/      → App seviyesi (AGENTS.md, CONTEXT.md, logs)
    │   ├── docs/       → AIDLC-lite (vision, tech-env, questions, design)
    │   └── app/        → Android kodu
    └── <app-b>/
        └── ...
```

### Miras Kuralları

- **App .kimi/AGENTS.md** → Proje AGENTS.md'yi bilir ama kendi kurallarını önceliklendirir
- **App .kimi/CONTEXT.md** → Sadece app durumunu tutar (proje CONTEXT.md'den bağımsız)
- **App docs/** → AIDLC-lite çalışma alanı (sorular, tasarım, kararlar)

### Yeni App Oluşturma

**Komut:**
```bash
cd /home/akn/local/projects/play-trend-hunter
cp -r apps/_template apps/<isim>
```

**Sonra Kimi otomatik şunları yapar:**
1. `apps/<isim>/_template`'den kopyalanan placeholder'ları (`<APP_NAME>`) gerçek app adıyla değiştirir
2. `apps/<isim>/.kimi/AGENTS.md` — App adını yazar
3. `apps/<isim>/.kimi/CONTEXT.md` — App adını yazar, durumu sıfırlar
4. `apps/<isim>/docs/*.md` — Placeholder'ları app adıyla değiştirir
5. `apps/<isim>/app/build.gradle.kts` — `namespace` ve `applicationId`'yi app'e göre ayarlar
6. `apps/<isim>/app/src/main/res/values/strings.xml` — `app_name`'i ayarlar

**AIDLC-lite akışı başlat:**
```text
apps/<isim>'de yeni app başlat. _template'ten fork edildi.
Trend sinyali: [app adı] — [kategori] — rank [X] → [Y]
AIDLC-lite akışına başla:
1. docs/vision.md yaz
2. docs/tech-env.md yaz
3. Sorularını docs/questions.md'ye yaz, dur
```

### App Seviyesi Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. `apps/<isim>/.kimi/CONTEXT.md` oku | 1. `apps/<isim>/.kimi/CONTEXT.md` güncelle |
| 2. `apps/<isim>/docs/questions.md` kontrol et | 2. `apps/<isim>/.kimi/logs/` session log yaz |
| 3. `apps/<isim>/docs/design.md` oku (kod değişikliği varsa) | 3. `apps/<isim>/docs/design.md` güncelle |
| 4. `apps/<isim>/.kimi/AGENTS.md` oku | 4. Build testi (`./gradlew assembleDebug`) |
| 5. Kullanıcıdan talimat al | 5. Git status kontrol et |

> AIDLC-lite detayları: `references/AIDLC-LITE.md`

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. AGENTS.md oku | 2. Session log yaz |
| 3. Skill oku (görev gerektiriyorsa) | 3. Skill güncelle (değişiklik varsa) |
| 4. Kullanıcıdan talimat al | 4. `run.py detect` çalıştır (veri değiştiyse) |
| | 5. Git status kontrol et |
