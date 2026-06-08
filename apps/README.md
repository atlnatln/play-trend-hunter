# App Factory

> `play-trend-hunter/apps/` — Her app kendi `.kimi/` context'i ve AIDLC-lite dokümanlarıyla bağımsız çalışır.

---

## Dizin Yapısı

```
apps/
├── README.md               → Bu dosya
├── _template/              → Yeni app şablonu (AIDLC-lite uyumlu)
│   ├── .kimi/
│   │   ├── AGENTS.md
│   │   ├── CONTEXT.md
│   │   └── logs/
│   ├── docs/
│   │   ├── vision.md
│   │   ├── tech-env.md
│   │   ├── questions.md
│   │   ├── design.md
│   │   └── decisions/
│   ├── app/
│   └── ...
├── digital-compass/        → İlk app (AIDLC-lite ile geliştiriliyor)
│   ├── .kimi/
│   ├── docs/
│   ├── app/
│   └── MVP.md
└── <gelecek-app>/          → Yeni app'ler buraya
    ├── .kimi/
    ├── docs/
    └── app/
```

---

## Yeni App Oluşturma

```bash
cd /home/akn/local/projects/play-trend-hunter
cp -r apps/_template apps/<app-adi>
```

Sonra Kimi'ye:
```text
apps/<app-adi>'de yeni app başlat. _template'ten fork edildi.
Trend sinyali: [app adı] — [kategori] — rank [X] → [Y]
AIDLC-lite akışına başla:
1. docs/vision.md yaz
2. docs/tech-env.md yaz
3. Sorularını docs/questions.md'ye yaz, dur
```

---

## Hiyerarşi

| Seviye | Dizin | Amaç |
|--------|-------|------|
| **Proje** | `play-trend-hunter/.kimi/` | Trend detection, scraper, detector kuralları |
| **App** | `apps/<isim>/.kimi/` | App-spesifik davranış, AIDLC-lite state |
| **Dokümantasyon** | `apps/<isim>/docs/` | AIDLC-lite çalışma alanı (vision, design, questions) |

---

## AIDLC-lite Akışı (App Başına)

```
docs/vision.md + docs/tech-env.md
    → docs/questions.md (sen cevapla)
    → docs/design.md (onayla)
    → kod planı (onayla)
    → kod → build → test
    → docs/design.md güncelle (geri yayım)
```

**Kritik Kural:** Kimi kafasına takılan bir şey varsa sohbette sormaz. `docs/questions.md`'ye yazar ve durur.

Detaylar: `references/AIDLC-LITE.md`
