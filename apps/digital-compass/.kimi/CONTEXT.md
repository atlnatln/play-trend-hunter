# Digital Compass — Aktif Context

> **AIDLC-lite State File.** Her session başında ilk okunan dosya.

---

## ⏭️ Açık Görevler

1. **Signing + Release build** — keystore oluştur, `./gradlew assembleRelease`, APK boyut < 5MB
2. **Play Console** — Yeni app kaydı, internal testing track
3. **Icon/Feature Graphic** — `flux-asset-generation` skill'i ile asset üretimi
4. **Emulator kurulumu** — Maestro test pipeline'ı için AVD oluştur

---

## ✅ Tamamlananlar

- [x] Android template fork'u
- [x] SensorManager + compass kodu
- [x] Dark theme UI
- [x] `./gradlew assembleDebug` → BUILD SUCCESSFUL (4s, 5.5MB APK)
- [x] Maestro test PASSED (emulator: Pixel_6_API_34)
- [x] `docs/vision.md` yazıldı
- [x] `docs/tech-env.md` yazıldı
- [x] `docs/design.md` yazıldı ve back-propagation yapıldı

---

## 🎯 Durum

**MVP kodu tamamlandı.** Build başarılı. Tasarım belgesi (`docs/design.md`) onaylı.

**Bekleyen kararlar:**
- Release signing key nasıl oluşturulacak? (mathlock-play'den kopyala vs yeni oluştur)
- Play Console app name: "Digital Compass" mu yoksa "Simple Compass: Ad-Free" mu?
- Feature graphic prompt'u ne olacak?

**Bugünkü rank:** 38 (stabilize) — momentum devam ediyor.

---

## 🐛 Aktif Sorunlar

| ID | Sorun | Öncelik |
|----|-------|---------|
| D2 | Release build yapılmadı | Yüksek |
| D3 | Play Console kaydı yok | Yüksek |

---

## 🔗 Hızlı Referanslar

| Konu | Dosya |
|------|-------|
| Tasarım (tek kaynak) | `docs/design.md` |
| Vizyon | `docs/vision.md` |
| Teknik ortam | `docs/tech-env.md` |
| Sorular | `docs/questions.md` |
| Proje factory kuralları | `../../AGENTS.md` |
| AIDLC-lite referans | `../../../../references/AIDLC-LITE.md` |
| Android/Maestro skill | `../../../.kimi/skills/android-test-pipeline/SKILL.md` |
