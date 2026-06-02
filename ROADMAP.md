# Play Trend Hunter — Stratejik Yol Haritası

> **Versiyon:** 1.0  
> **Tarih:** 2026-05-31 (Gün 1)  
> **Durum:** MVP tamamlandı, veri kalitesi doğrulandı, strateji başlatıldı.

---

## 🎯 Vizyon

Google Play Store'da yükselen uygulamaları **erken tespit edip**, her alt kategoride hızlıca "better clone" ürünleri çıkararak organik büyüme yakalamak.

**Temel Prensip:** Kategori seçimi değil, **momentum tespiti**. Sürünün gittiği yöne gitmek, ama daha hızlı ve daha iyi.

---

## 📊 Başarı Metrikleri

| Metrik | Hedef | Ölçüm Yöntemi |
|--------|-------|---------------|
| **Surge Tespit Doğruluğu** | %70+ true positive | Manuel doğrulama (haftalık) |
| **MVP Çıkış Süresi** | ≤ 7 gün (sinyal → Play Store upload) | Takvim takibi |
| **İlk 1000 İndirme** | ≤ 30 gün (soft launch sonrası) | Play Console |
| **Review Sentiment** | ≥ 4.0 yıldız ortalama | Play Console |
| **Portfolyo Boyutu** | 3 app (Ay 3 sonu) | Play Console |

---

## 🗓️ Fazlar

### Faz 0: Veri Birikimi ve Kalibrasyon (Hafta 1–2)

**Amaç:** Kendi momentum skorumuzu güvenilir hale getirmek.

| Görev | Süre | Çıktı |
|-------|------|-------|
| Günlük `run.py full` çalıştırma | 7–14 gün | 7–14 snapshot seti |
| False positive/negative analizi | Her hafta | Kalibre edilmiş threshold |
| "Newcomer" tanımı netleştirme | 1 gün | `released` son X ay = newcomer |
| İlk "ilginç" app tespiti | Sürekli | 3–5 aday app listesi |

**Rutin:**
```bash
# Her gün sabah
cd play-trend-hunter && source .venv/bin/activate && python run.py full
```

**Karar noktası (Hafta 2 sonu):**
- Surge threshold'u (`SURGE_THRESHOLD`) netleşmiş mi?
- En az 3 anlamlı sinyal yakaladık mı?
- → **Evet:** Faz 1'e geç. **Hayır:** Veri biriktirmeye devam et.

---

### Faz 1: İlk Fast-Follow (Hafta 3 – Ay 1 Sonu)

**Amaç:** Tek bir app'e odaklanarak "better clone" prensibini kanıtlamak.

| Adım | Süre | Açıklama |
|------|------|----------|
| 1. Sinyal seçimi | 1 gün | En yüksek surge score + en düşük rekabet |
| 2. Reverse engineering | 1–2 gün | App'i indir, oyna, 1-2★ review'ları oku |
| 3. Şikayet listesi | 0.5 gün | En sık tekrarlanan 3 şikayet |
| 4. MVP planı | 1 gün | Feature set, UI wireframe, ASO title |
| 5. Geliştirme | 3–5 gün | Flutter template + odağı çözülen 3 şikayet |
| 6. Soft launch | 3–7 gün | Internal + Closed testing, ASO optimize |
| 7. İterasyon | Sürekli | Review'lara göre polish |

**Teknoloji:**
- **Flutter** (tek kod tabanı, hızlı MVP, Play Store'a kolay build)
- **Firebase:** Analytics, Crashlytics, Remote Config
- **RevenueCat:** IAP entegrasyonu
- **AdMob:** Reklam entegrasyonu

**MVP Şablonları (Önceden hazırlanacak):**
- Hyper-casual oyun (Unity/Flutter)
- Utility app (Flutter + native bridge)
- Puzzle oyun (Flutter + grid engine)

---

### Faz 2: Template ve Otomasyon (Ay 2)

**Amaç:** İkinci ve üçüncü app'i daha hızlı çıkarmak.

| Görev | Süre | Çıktı |
|-------|------|-------|
| İlk app'ten ders çıkarma | 1 gün | "Bu app'te ne işe yaradı, ne yaramadı" |
| MVP şablonu oluşturma | 3–5 gün | Tekrar kullanılabilir Flutter base |
| Telegram alert botu | 2–3 gün | Surge alert → anlık bildirim |
| Review sentiment analizi | 3–5 gün | 1-2★ review'ları otomatik kategorize etme |
| İkinci app geliştirme | 7–10 gün | Faz 1 şablonu kullanarak |

**Otomasyon hedefi:**
```
Sinyal → Telegram Alert → Reverse Eng. → Şablon seç → MVP (≤ 5 gün) → Soft Launch
```

---

### Faz 3: Ölçek ve Portfolyo (Ay 3)

**Amaç:** Sürekli üretim hattına dönüştürmek.

| Görev | Süre | Çıktı |
|-------|------|-------|
| VPS cron kurulumu | 1 gün | Günlük otomatik `run.py full` + `detect` |
| Üçüncü app | 7–10 gün | Portfolyo çeşitliliği (farklı kategori) |
| ASO keyword tracking | 3–5 gün | Belirli keyword'lerde rank değişimi takibi |
| Sunsetting stratejisi | 1 gün | ASO'da patlamayan app'leri kaldırma kuralı |
| Dashboard (opsiyonel) | 5–7 gün | Basit web UI: alert'ler, app durumları |

**Portfolyo hedefi (Ay 3 sonu):**
- 3 aktif app (farklı kategorilerde)
- 1 app soft launch'ta
- Günlük otomatik tarama + alert

---

## 🔄 Günlük / Haftalık Rutin

### Her Gün (5 dk)
```bash
python run.py full        # scan + detect
python run.py alerts      # son alert'lere bak
```

### Her Hafta (30 dk)
1. Geçen haftaki alert'leri incele — true positive mi?
2. Aday app'leri değerlendir — hangisi fast-follow'a değer?
3. Aktif app'lerin Play Console verilerini kontrol et.
4. ROADMAP ve CONTEXT.md'yi güncelle.

### Her Ay (2 saat)
1. Faz hedeflerini değerlendir.
2. Threshold ve algoritma kalibrasyonu.
3. Yeni şablon / teknik kararlar.
4. Wiki'ye strateji kararlarını yaz.

---

## ⚠️ Riskler ve Önlemler

| Risk | Olasılık | Etki | Önlem |
|------|----------|------|-------|
| Google scraper parser kırılır | Orta | Yüksek | Parser'ı izle, community PR'larını takip et, Playwright fallback hazırla |
| IP ban | Orta | Yüksek | Proxy rotation ekle (Ay 2), cache TTL'yi uzat |
| App takedown (copyright) | Düşük | Yüksek | Orijinal asset, farklı isim, mekanik varyasyon |
| MVP 7 günde yetişmez | Orta | Orta | Scope kıs, "better clone" değil "mini clone" yap |
| Organik büyüme olmaz | Orta | Yüksek | ASO'ya odaklan, TikTok/Shorts viral mekanikleri ekle |
| Tek kişi, çok app bakımı | Yüksek | Orta | ASO'da patlayanlara odaklan, gerisini sunset |

---

## 🗂️ Karar Kayıtları (ADR)

| Tarih | Karar | Gerekçe |
|-------|-------|---------|
| 2026-05-31 | API tabanlı scraping (Node.js) | Playwright'tan daha hızlı, daha az kaynak, daha az ban riski |
| 2026-05-31 | Hibrit hafıza (Wiki + `.kimi/`) | Wiki = strateji/cross-project; `.kimi/` = agent context/teknik ref |
| ~~2026-05-31~~ | ~~Flutter MVP şablonu~~ | ~~İPTAL: Mevcut Kotlin pipeline'ı (mathlock-play) daha değerli. Dart öğrenme eğrisi + yeni pipeline = zaman kaybı~~ |
| 2026-06-02 | **Kotlin Native Android** MVP şablonu | Mevcut mathlock-play pipeline'ı (Gradle, Keystore, Play Console, deploy.sh) kopyalanabilir. APK boyutu küçük, Play Store performansı en iyi |
| 2026-06-02 | **Maestro** mobil test framework'ü | Agent (Kimi) YAML test'leri yazabilir ve shell'den çalıştırabilir. Assertion sonuçlarını analiz edebilir. Görsel/oyun testleri için manuel test gerekir |
| 2026-06-02 | **Web tabanlı app yapılmayacak** | Hedef Google Play Store. Web wrapper (Capacitor/PWA) "low quality" etiketi riski. Aday app web tabanlı olsa bile native Kotlin clone yapılacak |
| 2026-05-31 | SQLite (yerel DB) | Hafif, bakım yok, yeterli ölçek |

---

> **Sonraki Adım:** Faz 0 başlat — 7 gün veri biriktir. Her gün `run.py full` çalıştır, alert'leri izle.
