# AGENTS.md — <APP_NAME>

> ⚠️ **BU DOSYA `_template` İÇİNDEDİR.** Yeni app oluşturulduğunda Kimi otomatik olarak `<APP_NAME>` yerine gerçek app adını yazar.
>
> **Hiyerarşi:** `play-trend-hunter/AGENTS.md` (app factory) → bu dosya (app-spesifik).  
> **AIDLC-lite:** Bu app AIDLC-lite sistemiyle yönetilir. `references/AIDLC-LITE.md` oku.

---

## 📖 Okuma Sırası (Her Session)

1. `.kimi/CONTEXT.md` — Aktif durum, açık sorular, sıradaki görev
2. `docs/questions.md` — Cevap bekleyen sorular var mı?
3. `docs/design.md` — Onaylanmış tasarım (kod için tek kaynak)
4. Bu dosya (AGENTS.md) — Davranış kuralları

---

## 🔄 AIDLC-lite Akışı

```
docs/vision.md + docs/tech-env.md
    → docs/questions.md (sen cevapla)
    → docs/design.md (onayla)
    → kod planı (onayla)
    → kod → build → test
    → docs/design.md güncelle (geri yayım)
```

**Kritik Kurallar:**

1. **Soru → Belge → Onay:** Kafana takılan bir şey varsa sohbette sorma. `docs/questions.md`'ye yaz ve dur.
2. **"Hiçbir belgeyi güncelleme" ile keşif:** Keşif amaçlı sorulara bu cümleyle başla.
3. **Bağlamı her geçitte temizle:** Soru cevaplandığında / tasarım onaylandığında yeni session başlat.
4. **Tasarım öncelikli:** Asla doğrudan kod düzenleme. Önce `docs/design.md`, sonra kod.
5. **Prompt toplama:** İlişkili değişiklikler tek prompt'ta.

---

## 🛠️ Android Kuralları

| Konu | Kural |
|------|-------|
| **Build** | Her değişiklik sonrası `./gradlew assembleDebug` zorunlu |
| **Maestro** | Emulator'de çalıştır: `maestro test maestro/launch.yaml` |
| **Signing** | Release için `keystore.jks` + `local.properties`. `.gitignore`'da |
| **Min SDK** | 26 (Android 8.0) — sabit |
| **Theme** | Material3 Dark NoActionBar — sabit |

---

## 🧭 Oturum Protokolü

| Başlangıç | Bitiş |
|-----------|-------|
| 1. CONTEXT.md oku | 1. CONTEXT.md güncelle |
| 2. questions.md kontrol et | 2. Session log yaz (.kimi/logs/) |
| 3. AGENTS.md oku | 3. design.md güncelle (değişiklik varsa) |
| 4. Kullanıcıdan talimat al | 4. Build testi (kod değiştiyse) |
| | 5. Git status kontrol et |
