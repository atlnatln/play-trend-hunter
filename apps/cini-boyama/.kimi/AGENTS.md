# AGENTS.md — Çini Boyama

> App-spesifik kurallar. Proje seviyesi kurallar için `play-trend-hunter/AGENTS.md`.

---

## 🎯 App Kimliği

- **Klasör:** `apps/cini-boyama/`
- **Türkçe Ad:** Çini Boyama
- **İngilizce Ad:** Iznik Tile Coloring
- **Package:** `com.akn.ciniboyama`
- **Kategori:** ART_AND_DESIGN

---

## 📖 Çalışma Akışı

1. `.kimi/CONTEXT.md` oku
2. `docs/design.md` oku (kod için tek kaynak)
3. `docs/questions.md` kontrol et
4. Kod değişikliği varsa önce `design.md` güncelle
5. Build/test (`./gradlew assembleDebug`) → Maestro (`maestro/`) → log yaz

---

## 🎨 MVP Kapsamı

- Hazır çini desenleri (asset, 4 adet)
- Boyama ekranı (flood fill + renk paleti)
- Sır (glaze) efekti toggle'ı
- Basit ilerleme kaydı (SharedPreferences)
- Maestro smoke test

## 🚫 Kapsam Dışı (Sonra)

- Kamera / import
- Ses/ASMR
- Çatlak (craquelure) efekti
- IAP / reklam
- Çoklu dil
