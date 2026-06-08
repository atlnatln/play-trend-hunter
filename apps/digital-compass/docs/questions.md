# Digital Compass — AIDLC Sorular ve Cevaplar

> AIDLC-lite: Kimi buraya sorular yazar, kullanıcı `[Cevap]:` satırlarını doldurur.

---

## Soru 1: Play Store Title
Play Store'da hangi title kullanalım?

A) Digital Compass
B) Digital Compass — Accurate & No Ads
C) Simple Compass: Ad-Free
D) Digital Compass Pro — Minimal & Fast

[Cevap]: B — "Accurate & No Ads" en büyük farkımızı vurguluyor, ASO'da "compass" + "no ads" keyword'lerini yakalıyor.

---

## Soru 2: Pusula İğnesi vs Sadece Derece
UI'da pusula iğnesi (ImageView rotate) mi yoksa sadece büyük derece + yön adı mı?

A) Pusula iğnesi (visually richer)
B) Sadece derece + yön adı (minimal, daha az kod)
C) Her ikisi (derece büyük, altında küçük iğne)

[Cevap]: B — minimal MVP. Sadece derece + yön adı. Pusula iğnesi v1.1'de eklenebilir.

---

## Soru 3: Signing Key
Release signing key'i nasıl oluşturalım?

A) mathlock-play'den mevcut keystore'u kopyala
B) Yeni keystore oluştur (dedicated for Digital Compass)

[Cevap]: B — Her app'in kendi signing key'i olmalı. `keytool -genkey` ile yeni oluştur.

---

## Soru 4: Kalibrasyon Uyarısı
Cihaz manyetik alan kalibrasyonu gerekirse kullanıcıya uyarı gösterelim mi?

A) Evet, kalibrasyon gerekirse Toast/Snackbar göster
B) Hayır, MVP'de kalibrasyon uyarısı yok

[Cevap]: B — MVP'de yok. v1.1'de eklenebilir. Şimdilik sadece temel pusula.

---

> **Tüm sorular cevaplandı.** Kimi devam edebilir.
