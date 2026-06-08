# Digital Compass — Teknik Ortam Belgesi

## Dil ve Sürüm

- **Dil:** Kotlin
- **Min SDK:** 26 (Android 8.0)
- **Target SDK:** 35
- **Compile SDK:** 35

## Framework ve Kütüphaneler

| Kategori | Seçim | Versiyon |
|----------|-------|----------|
| UI Framework | Android View + ViewBinding | — |
| Layout | ConstraintLayout | 2.1.4 |
| Theme | Material3 | 1.11.0 |
| Core | AndroidX KTX | 1.12.0 |
| Test | JUnit + Espresso | 4.13.2 / 3.5.1 |

## Deploy Modeli

- **Yerel build:** `./gradlew assembleRelease`
- **Dağıtım:** Google Play Store (Internal → Closed → Production)
- **CI/CD:** Manuel build + upload (MVP aşamasında)

## Yasaklı Kütüphaneler

| Kütüphane | Neden Yasak | Alternatif |
|-----------|-------------|------------|
| Google Mobile Ads (AdMob) | Zero ads prensibi | Yok (reklam yok) |
| Location Services | Gereksiz izin | Yok (sadece sensör) |
| CameraX | Gereksiz izin | Yok |
| Play Services (gereksiz) | APK boyutu, izin | SensörManager (native) |

## Örnek Kod Kalıpları

### Sensor Event Listener (MainActivity.kt)

```kotlin
class MainActivity : AppCompatActivity(), SensorEventListener {
    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null
    private var magnetometer: Sensor? = null

    override fun onSensorChanged(event: SensorEvent) {
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> System.arraycopy(event.values, 0, accelReading, 0, 3)
            Sensor.TYPE_MAGNETIC_FIELD -> System.arraycopy(event.values, 0, magnetReading, 0, 3)
        }
        if (SensorManager.getRotationMatrix(rotationMatrix, null, accelReading, magnetReading)) {
            SensorManager.getOrientation(rotationMatrix, orientationAngles)
            val azimuth = Math.toDegrees(orientationAngles[0].toDouble()).toFloat()
            val degrees = ((azimuth + 360) % 360).toInt()
            // UI güncelle
        }
    }
}
```

### Layout (activity_main.xml)

```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView android:id="@+id/tv_degrees" android:textSize="96sp" />
    <TextView android:id="@+id/tv_direction" android:textSize="48sp" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

## Güvenlik

- `android:allowBackup="false"`
- Keystore `.gitignore`'da
- `local.properties` `.gitignore`'da
