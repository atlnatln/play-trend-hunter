# Çini Boyama — Onaylanmış Tasarım

> AIDLC-lite: Bu belge kod için tek doğru kaynaktır.

---

## 1. Genel Tasarım

Tek ekranlı MVP:
1. **MainActivity** — Desen seçim grid'i
2. **ColorActivity** — Boyama ekranı (desen + palet + efekt)

Tema: Koyu arka plan (`#1A1A2E`), altın vurgu rengi (`#D4AF37`), çini mavi aksan (`#1E3A8A`).

---

## 2. UI Layout

### 2.1 MainActivity (`activity_main.xml`)

- `Toolbar` — App başlığı "Çini Boyama"
- `RecyclerView` — 2 sütunlu grid, 4 kart
- Her kart:
  - `ImageView` — Desen önizlemesi (renkli orijinal, 1:1)
  - `TextView` — Desen adı (örn. "İznik Mandala")

### 2.2 ColorActivity (`activity_color.xml`)

- `Toolbar` — Geri butonu + desen adı + "0/12 tamamlandı" metni
- `ColoringView` (custom) — Boyanabilir line art (match_parent, üst-altta margin)
- Alt panel:
  - `RecyclerView` — Yatay renk paleti (yuvarlak renk butonları)
  - `MaterialButtonToggleGroup` — Sır efekti ON/OFF
  - `MaterialButton` — Temizle

### 2.3 Renk Paleti

12 klasik çini rengi:
```xml
<array name="cini_colors">
    <item>#1E3A8A</item> <!-- Kobalt Mavi -->
    <item>#0EA5E9</item> <!-- Turkuaz -->
    <item>#047857</item> <!-- Yeşil -->
    <item>#B91C1C</item> <!-- Kırmızı -->
    <item>#F59E0B</item> <!-- Sarı/Altın -->
    <item>#FEF3C7</item> <!-- Krem -->
    <item>#FFFFFF</item> <!-- Beyaz -->
    <item>#111827</item> <!-- Siyah kontur -->
    <item>#7C3AED</item> <!-- Mor -->
    <item>#EC4899</item> <!-- Pembe -->
    <item>#92400E</item> <!-- Kahve -->
    <item>#D4AF37</item> <!-- Altın -->
</array>
```

---

## 3. İş Mantığı

### 3.1 MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    private val patterns = listOf(
        Pattern(R.drawable.preview_iznik_tile, R.drawable.lineart_iznik_tile, "İznik Mandala"),
        Pattern(R.drawable.preview_iznik_vase, R.drawable.lineart_iznik_vase, "İznik Vazo"),
        Pattern(R.drawable.preview_geometric, R.drawable.lineart_geometric, "Geometrik"),
        Pattern(R.drawable.preview_flower, R.drawable.lineart_flower, "Gül Deseni"),
    )
}
```

Tıklanınca:
```kotlin
val intent = Intent(this, ColorActivity::class.java)
intent.putExtra("lineart_res", pattern.lineartRes)
intent.putExtra("title", pattern.title)
startActivity(intent)
```

### 3.2 ColorActivity

- `lineart_res`'i `ColoringView`'e set et
- Seçili rengi `ColoringView.selectedColor`'a ata
- Sır toggle'ı `ColoringView.setGlazeEnabled(Boolean)` çağırır
- Temizle butonu `ColoringView.reset()` çağırır
- İlerleme: `ColoringView.onProgressListener = { filled, total -> ... }`

### 3.3 ColoringView (Custom View)

```kotlin
class ColoringView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private lateinit var baseBitmap: Bitmap      // Line art (siyah hatlar, beyaz bölgeler)
    private lateinit var coloredBitmap: Bitmap   // Boyanmış kopya
    private var selectedColor: Int = Color.BLUE
    private var glazeEnabled: Boolean = false

    override fun onDraw(canvas: Canvas) {
        canvas.drawBitmap(coloredBitmap, 0f, 0f, null)
        if (glazeEnabled) drawGlazeOverlay(canvas)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.action == MotionEvent.ACTION_DOWN) {
            val x = event.x.toInt()
            val y = event.y.toInt()
            if (x in 0 until coloredBitmap.width && y in 0 until coloredBitmap.height) {
                floodFill(coloredBitmap, x, y, selectedColor)
                invalidate()
            }
            return true
        }
        return super.onTouchEvent(event)
    }
}
```

### 3.4 Flood Fill

Queue-based BFS. Eşik: dokunulan pikselin rengi `targetColor` ise ve beyaz/boş alandaysa (`targetColor` ≈ `Color.WHITE`), boya.

```kotlin
private fun floodFill(bitmap: Bitmap, x: Int, y: Int, fillColor: Int) {
    val targetColor = bitmap.getPixel(x, y)
    if (targetColor == fillColor) return
    if (!isFillable(targetColor)) return

    val w = bitmap.width
    val h = bitmap.height
    val queue = ArrayDeque<Pair<Int, Int>>()
    queue.add(x to y)

    while (queue.isNotEmpty()) {
        val (cx, cy) = queue.removeFirst()
        if (cx < 0 || cx >= w || cy < 0 || cy >= h) continue
        if (bitmap.getPixel(cx, cy) != targetColor) continue
        bitmap.setPixel(cx, cy, fillColor)
        queue.add(cx + 1 to cy)
        queue.add(cx - 1 to cy)
        queue.add(cx to cy + 1)
        queue.add(cx to cy - 1)
    }
}
```

`isFillable(color)`: Renkli bölge değilse (siyah kontur veya zaten boyanmışsa) boyama.

### 3.5 Sır (Glaze) Efekti

Boyanan bölgeye yarı saydam parlaklık overlay:

```kotlin
private fun drawGlazeOverlay(canvas: Canvas) {
    val paint = Paint().apply {
        color = Color.WHITE
        alpha = 60
        xfermode = PorterDuffXfermode(PorterDuff.Mode.OVERLAY)
    }
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

Gelişmiş versiyonda: sadece boyanmış bölgelere uygulanabilir (mask bitmap).

---

## 4. Permissions & Manifest

- **Hiçbir izin yok.** MVP internet, depolama, kamera kullanmaz.
- `AndroidManifest.xml`'de iki activity declare edilir:
  - `MainActivity` (exported, launcher)
  - `ColorActivity` (exported=false)

---

## 5. Build Konfigürasyonu

```kotlin
android {
    namespace = "com.akn.ciniboyama"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.akn.ciniboyama"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
}
```

---

## 6. Dosya Yapısı

```
app/src/main/
├── AndroidManifest.xml
├── java/com/akn/ciniboyama/
│   ├── MainActivity.kt
│   ├── ColorActivity.kt
│   ├── ColoringView.kt
│   ├── Pattern.kt
│   └── PatternAdapter.kt
├── res/
│   ├── drawable/
│   │   ├── preview_iznik_tile.png
│   │   ├── lineart_iznik_tile.png
│   │   └── ... (4×2 = 8 asset)
│   ├── layout/
│   │   ├── activity_main.xml
│   │   ├── activity_color.xml
│   │   ├── item_pattern.xml
│   │   └── item_color.xml
│   ├── values/
│   │   ├── colors.xml
│   │   ├── strings.xml
│   │   └── themes.xml
│   └── menu/
│       └── (yok)
└── maestro/
    └── launch.yaml
```

---

## 7. Test Planı

| Test | Yöntem | Beklenen |
|------|--------|----------|
| App açılır | Maestro `launch.yaml` | MainActivity görünür |
| Desen seçimi | Maestro tap | ColorActivity açılır |
| Boyama | Manuel | Dokunulan bölge renk değiştirir |
| Sır toggle | Manuel | Ekranda parlak overlay belirir |
| Temizle | Manuel | Tüm bölgeler beyaz/varsayılan olur |
| Build | Gradle | `assembleDebug` başarılı |

---

## 8. Değişiklik Geçmişi

| Tarih | Değişiklik | Kim |
|-------|-----------|-----|
| 2026-06-10 | İlk tasarım | kimi-agent |
