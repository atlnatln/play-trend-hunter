# AGENTS.md — Digital Compass

> **Hiyerarşi:** `play-trend-hunter/AGENTS.md` (app factory) → bu dosya (app-spesifik).  
> **AIDLC-lite:** Bu app AIDLC-lite sistemiyle yönetilir. `references/AIDLC-LITE.md` oku.

---

## 📖 Okuma Sırası (Her Session)

1. `.kimi/CONTEXT.md` — Aktif durum, açık sorular, sıradaki görev
2. `docs/questions.md` — Cevap bekleyen sorular var mı?
3. `docs/design.md` — Onaylanmış tasarım (kod için tek kaynak)
4. Bu dosya (AGENTS.md) — Davranış kuralları

**Sadece detay gerekiyorsa:** `docs/vision.md`, `docs/tech-env.md`, `MVP.md`, session log'ları.

---

## 🔄 AIDLC-lite Akışı

Bu app AIDLC-lite ile geliştirilir:

```
docs/vision.md + docs/tech-env.md
    → docs/questions.md (sen cevapla)
    → docs/design.md (onayla)
    → kod planı (onayla)
    → kod → build → test
    → docs/design.md güncelle (geri yayım)
```

**Kritik Kurallar:**

1. **Soru → Belge → Onay:** Kafana takılan bir şey varsa sohbette sorma. `docs/questions.md`'ye yaz ve dur. Kullanıcı cevap verene kadar bekle.
2. **"Hiçbir belgeyi güncelleme" ile keşif:** Keşif amaçlı sorulara bu cümleyle başla. Taahhüte hazır olduğunda kısıtlamayı kaldır.
3. **Bağlamı her geçitte temizle:** Soru cevaplandığında / tasarım onaylandığında yeni session başlat. "Dosyayı yeniden oku ve devam et."
4. **Tasarım öncelikli:** Asla doğrudan kod düzenleme. Önce `docs/design.md`, sonra kod.
5. **Prompt toplama:** İlişkili değişiklikler tek prompt'ta.

---

## 🛠️ Android Kuralları

| Konu | Kural |
|------|-------|
| **Build** | Her değişiklik sonrası `./gradlew assembleDebug` zorunlu |
| **Emulator** | `emulator -avd Pixel_6_API_34 -no-window -no-audio -gpu swiftshader_indirect &` (PATH: `$ANDROID_HOME/emulator`) |
| **Maestro** | Emulator başlayınca: `adb install -r app/build/outputs/apk/debug/app-debug.apk`, sonra `maestro test maestro/launch.yaml` |
| **Signing** | Release için `keystore.jks` + `local.properties`. `.gitignore`'da |
| **Min SDK** | 26 (Android 8.0) — sabit |
| **Theme** | Material3 Dark NoActionBar — sabit |
| **Permissions** | Sadece sensör. Fotoğraf, konum, medya İZİN İSTEMEZ |
| **Ads** | ZERO reklam. Bu app'in en büyük farkı |

---

## 📁 Dosya Yapısı

```
apps/digital-compass/
├── .kimi/
│   ├── AGENTS.md          → Bu dosya
│   ├── CONTEXT.md         → Aktif durum
│   └── logs/              → Session logları
├── docs/
│   ├── vision.md          → Ne ve neden
│   ├── tech-env.md        → Stack + kısıtlar
│   ├── questions.md       → AIDLC soruları + cevaplar
│   ├── design.md          → Onaylanmış tasarım
│   └── decisions/         → ADR'lar
├── app/                   → Android kodu
└── MVP.md                 → Strateji dokümanı (AIDLC dışı)
```

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. questions.md kontrol et | 2. Session log yaz (.kimi/logs/) |
| 3. AGENTS.md oku | 3. design.md güncelle (değişiklik varsa) |
| 4. Kullanıcıdan talikat al | 4. Build testi (kod değiştiyse) |
| | 5. Git status kontrol et |
