---
name: android-test-pipeline
description: Kotlin Android build pipeline, Maestro E2E test, emulator yonetimi, fast-follow app olusturma
metadata:
  last_updated: 2026-06-03
  maestro_version: "2.6.0"
  emulator: "Pixel_6_API_34"
  agp: "8.2.2"
  kotlin: "1.9.20"
---

# Android Test Pipeline — Teknik Referans

> Ana proje referansı: `play-trend-hunter` skill. Bu dosya = Android geliştirme ve test özel.

---

## 1. Maestro Kurulumu ve Kullanımı

```bash
# Kurulum
curl -fsSL "https://get.maestro.mobile.dev" | bash
export PATH="$PATH:$HOME/.maestro/bin"
maestro --version   # 2.6.0+
```

**Temel Komutlar:**
```bash
maestro test flow.yaml              # Tek flow çalıştır
maestro test flows/                 # Tüm flow'ları çalıştır
maestro hierarchy                   # UI hiyerarşisi (element inspection)
maestro record flow.yaml            # Video kaydı
```

**Basit Flow Örneği:**
```yaml
appId: com.example.myapp
---
- launchApp
- tapOn: "Start Game"
- assertVisible: "Level 1"
- inputText: "Player1"
- tapOn: "Submit"
- assertVisible: "Score: 0"
```

**Visibility Assertions:**
```yaml
- assertVisible:
    text: ".*error.*"          # Regex match
- assertVisible:
    text: "Tooltip"
    optional: true              # Yoksa PASS
- assertNotVisible: "Loading..."
- assertVisible:
    text: "Price: $9.99"
    below:
      text: "Sauce Labs Backpack"
```

---

## 2. Android Emulator Yönetimi

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$HOME/.maestro/bin"

# Mevcut AVD'leri listele
emulator -list-avds

# AVD başlat (headless, arka planda)
emulator -avd Pixel_6_API_34 -no-window -no-audio -gpu swiftshader_indirect &

# Cihaz bağlı mı kontrol et
adb devices

# APK yükle
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Logcat izle
adb logcat -s com.example.myapp:D
```

**Mevcut AVD'ler:**
| AVD | Boyut | API | Durum |
|-----|-------|-----|-------|
| `Pixel_6_API_34` | 1080×2400 | 34 | ✅ Aktif test cihazı |
| `tablet_7inch` | 1200×1920 | 34 | Mevcut (eski) |
| `tablet_10inch` | — | 34 | Mevcut (eski) |

**AVD oluşturma (gerekirse):**
```bash
avdmanager create avd -n Pixel_6_API_34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6
```

---

## 3. Kotlin Android Build Pipeline

### Mevcut Pipeline

```bash
cd projects/mathlock-play   # veya android-template
./gradlew assembleDebug      # Debug APK (~10 sn - 1 dk)
./gradlew assembleRelease    # Release APK (keystore gerekir)
```

**Gerekli ortam değişkenleri:**
```bash
export ANDROID_HOME="$HOME/Android/Sdk"
```

**local.properties:**
```properties
sdk.dir=/home/akn/Android/Sdk
```

### APK Yükleme ve Test Döngüsü

```bash
# 1. Build
./gradlew assembleDebug

# 2. Yükle
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 3. Maestro test
maestro test maestro/launch.yaml

# 4. Crash kontrolü
adb logcat -d | grep AndroidRuntime
```

---

## 4. Android Template Yapısı (`android-template/`)

**Package:** `com.akn.playtrendhunter`  
**App name:** "Play Trend Hunter"  
**MinSdk:** 26 (Oreo)  
**CompileSdk:** 35  
**AGP:** 8.2.2 | **Kotlin:** 1.9.20

**Bağımlılıklar (sadece temel):**
| Kütüphane | Amaç |
|-----------|------|
| `androidx.core:core-ktx:1.12.0` | Kotlin extension'ları |
| `androidx.appcompat:appcompat:1.6.1` | AppCompat Activity |
| `com.google.android.material:material:1.11.0` | Material3 bileşenleri |
| `androidx.constraintlayout:constraintlayout:2.1.4` | Layout |
| `junit:junit:4.13.2` | Unit test |
| `androidx.test.espresso:espresso-core:3.5.1` | UI test |

**Çıkarılan bağımlılıklar (mathlock-play'den sadeleştirme):**
Billing, MPAndroidChart, ACRA, Biometric, Security-Crypto, RecyclerView, CardView, Lifecycle-Service

**Build özellikleri:**
- `viewBinding = true`
- `buildConfig = false`
- Release: `isMinifyEnabled = false` (MVP aşamasında)

---

## 5. Yeni Fast-Follow App Oluşturma Akışı

```bash
# 1. Template'i kopyala
cp -r android-template apps/<app-name>

# 2. Değiştirilmesi gerekenler
cd apps/<app-name>
# - settings.gradle.kts → rootProject.name
# - app/build.gradle.kts → namespace, applicationId, versionCode, versionName
# - app/src/main/res/values/strings.xml → app_name
# - app/src/main/java/com/akn/playtrendhunter/ → yeni package dizini

# 3. Build doğrula
./gradlew assembleDebug
```

**Değişiklik kontrol listesi:**
- [ ] `namespace = "com.akn.<appname>"` (app/build.gradle.kts)
- [ ] `applicationId = "com.akn.<appname>"` (app/build.gradle.kts)
- [ ] `rootProject.name = "<AppName>"` (settings.gradle.kts)
- [ ] `<string name="app_name">...</string>` (strings.xml)
- [ ] Package dizin yapısı ve `package` deklarasyonu (Kotlin dosyaları)
- [ ] `./gradlew assembleDebug` başarılı
- [ ] `maestro test maestro/launch.yaml` başarılı

---

## 6. Play Store Release Pipeline

```bash
# Keystore ile release build
./gradlew bundleRelease

# Play Store internal track upload (deploy.sh)
bash deploy.sh --track internal
```

> Play Trend Hunter app'lerinde mathlock-play'in aynı pipeline'ı kullanılacak. `deploy.sh`, `keystore.jks`, `play-console.json` dosyaları template olarak kopyalanabilir.

**Signing:**
- Release build için `keystore.jks` ve `local.properties` (şifreler) gerekir.
- `.gitignore`'da `*.jks`, `local.properties` var.
- Keystore mathlock-play'den kopyalanabilir.

---

## 7. Test Stratejisi — Agent vs Kullanıcı

| Test Türü | Kim Yapar? | Araç | Neden? |
|-----------|-----------|------|--------|
| **Unit test** | Agent | JUnit (Kotlin) | Kod doğruluğu |
| **Smoke test** (app açılıyor mu?) | Agent | Maestro YAML | Otomasyon |
| **Flow test** (login → oyna → skor) | Agent | Maestro YAML | Regression |
| **Assertion/log analizi** | Agent | Maestro output + logcat | Metin tabanlı |
| **Animasyon/oyun mekaniği** | **Kullanıcı** | Manuel oynama | Agent VLM değil, görsel analiz yapamaz |
| **Renk/UI estetiği** | **Kullanıcı** | Manuel gözlem | Agent renk/aydınlatma yorumu yapamaz |
| **Crash/bug analizi** | Agent | Logcat + Maestro log | Metin tabanlı |

**Önemli:** Agent metin-tabanlı LLM'dir. Screenshot'tan "bu buton yanlış yerde", "animasyon donuyor", "renk soluk" analizi **yapamaz** (VLM hariç). Bu tür testler kullanıcıya bırakılır.
