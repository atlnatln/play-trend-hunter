package com.akn.ciniboyama

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.PorterDuffXfermode
import android.graphics.RectF
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.util.AttributeSet
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.View
import androidx.annotation.DrawableRes
import androidx.core.content.ContextCompat
import androidx.core.content.getSystemService
import androidx.core.graphics.withSave
import kotlin.math.abs
import java.util.ArrayDeque

class ColoringView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var baseBitmap: Bitmap? = null
    private var coloredBitmap: Bitmap? = null
    private val drawBounds = RectF()
    private val drawMatrix = Matrix()
    private val inverseMatrix = Matrix()

    var selectedColor: Int = Color.BLUE
    var glazeEnabled: Boolean = false
        private set

    var onProgressChanged: ((filled: Int, total: Int) -> Unit)? = null

    private var totalFillablePixels: Int = 0
    private var filledPixels: Int = 0

    private val glazePaint = Paint().apply {
        color = Color.WHITE
        alpha = 180
        xfermode = PorterDuffXfermode(PorterDuff.Mode.OVERLAY)
        isAntiAlias = true
    }

    // Zoom / Pan state
    private var zoomScale = 1f
    private var panX = 0f
    private var panY = 0f
    private val zoomMatrix = Matrix()
    private val zoomInverseMatrix = Matrix()

    // Touch state
    private var touchStartX = 0f
    private var touchStartY = 0f
    private var hasTouchMoved = false
    private val TOUCH_SLOP = 16f

    private val scaleGestureDetector = ScaleGestureDetector(context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                val oldScale = zoomScale
                zoomScale *= detector.scaleFactor
                zoomScale = zoomScale.coerceIn(1.0f, 5.0f)
                // İki parmağın ortası (focus) sabit kalsın
                val focusX = detector.focusX
                val focusY = detector.focusY
                panX = focusX - (focusX - panX) * (zoomScale / oldScale)
                panY = focusY - (focusY - panY) * (zoomScale / oldScale)
                clampPan()
                recomputeZoomMatrix()
                invalidate()
                return true
            }
        })

    private val gestureDetector = GestureDetector(context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onScroll(
                e1: MotionEvent?, e2: MotionEvent,
                distanceX: Float, distanceY: Float
            ): Boolean {
                if (zoomScale > 1f) {
                    panX -= distanceX
                    panY -= distanceY
                    clampPan()
                    recomputeZoomMatrix()
                    invalidate()
                    return true
                }
                return false
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                if (zoomScale > 1f) {
                    resetZoom()
                } else {
                    val focusX = e.x
                    val focusY = e.y
                    val newScale = 3f
                    panX = focusX - (focusX - panX) * (newScale / zoomScale)
                    panY = focusY - (focusY - panY) * (newScale / zoomScale)
                    zoomScale = newScale
                    clampPan()
                    recomputeZoomMatrix()
                }
                invalidate()
                return true
            }
        })

    fun setPattern(@DrawableRes resId: Int) {
        if (resId == -1) return
        val drawable = ContextCompat.getDrawable(context, resId) ?: return
        val w = drawable.intrinsicWidth.coerceAtLeast(1)
        val h = drawable.intrinsicHeight.coerceAtLeast(1)
        val bitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, w, h)
        drawable.draw(canvas)

        baseBitmap = bitmap
        coloredBitmap = bitmap.copy(Bitmap.Config.ARGB_8888, true)
        totalFillablePixels = countFillablePixels(bitmap)
        filledPixels = countFilledPixels(coloredBitmap!!)
        resetZoom()
        notifyProgress()
        invalidate()
    }

    fun setGlazeEnabled(enabled: Boolean) {
        glazeEnabled = enabled
        invalidate()
    }

    fun reset() {
        val base = baseBitmap ?: return
        coloredBitmap = base.copy(Bitmap.Config.ARGB_8888, true)
        filledPixels = 0
        notifyProgress()
        invalidate()
    }

    private fun resetZoom() {
        zoomScale = 1f
        panX = 0f
        panY = 0f
        recomputeZoomMatrix()
    }

    private fun recomputeZoomMatrix() {
        zoomMatrix.reset()
        zoomMatrix.postScale(zoomScale, zoomScale)
        zoomMatrix.postTranslate(panX, panY)
        zoomMatrix.invert(zoomInverseMatrix)
    }

    private fun clampPan() {
        // Sadece zoom yoksa resetle; zoom varken serbest kaydır
        if (zoomScale <= 1f) {
            panX = 0f
            panY = 0f
        }
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        recalcMatrix()
    }

    private fun recalcMatrix() {
        val bmp = baseBitmap ?: return
        val bmpW = bmp.width.toFloat()
        val bmpH = bmp.height.toFloat()
        val viewW = width.toFloat()
        val viewH = height.toFloat()

        val scale = minOf(viewW / bmpW, viewH / bmpH)
        val dx = (viewW - bmpW * scale) / 2f
        val dy = (viewH - bmpH * scale) / 2f

        drawBounds.set(dx, dy, dx + bmpW * scale, dy + bmpH * scale)

        drawMatrix.setRectToRect(
            RectF(0f, 0f, bmpW, bmpH),
            drawBounds,
            Matrix.ScaleToFit.FILL
        )
        drawMatrix.invert(inverseMatrix)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val bmp = coloredBitmap ?: return
        canvas.withSave {
            canvas.translate(panX, panY)
            canvas.scale(zoomScale, zoomScale)
            canvas.drawBitmap(bmp, null, drawBounds, null)
            if (glazeEnabled) {
                canvas.drawRect(drawBounds, glazePaint)
            }
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        gestureDetector.onTouchEvent(event)
        scaleGestureDetector.onTouchEvent(event)

        if (scaleGestureDetector.isInProgress) {
            hasTouchMoved = true
            return true
        }

        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                touchStartX = event.x
                touchStartY = event.y
                hasTouchMoved = false
                parent?.requestDisallowInterceptTouchEvent(true)
            }
            MotionEvent.ACTION_MOVE -> {
                if (abs(event.x - touchStartX) > TOUCH_SLOP ||
                    abs(event.y - touchStartY) > TOUCH_SLOP
                ) {
                    hasTouchMoved = true
                }
            }
            MotionEvent.ACTION_UP -> {
                if (!hasTouchMoved) {
                    performFloodFill(event.x, event.y)
                }
                parent?.requestDisallowInterceptTouchEvent(false)
            }
            MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
            }
        }
        return true
    }

    private fun performFloodFill(viewX: Float, viewY: Float) {
        val bmp = coloredBitmap ?: return

        // 1. Undo zoom/pan
        val zoomPts = floatArrayOf(viewX, viewY)
        zoomInverseMatrix.mapPoints(zoomPts)
        // 2. Undo draw matrix (bitmap coords)
        val bmpPts = floatArrayOf(zoomPts[0], zoomPts[1])
        inverseMatrix.mapPoints(bmpPts)

        val bx = bmpPts[0].toInt()
        val by = bmpPts[1].toInt()

        if (bx in 0 until bmp.width && by in 0 until bmp.height) {
            val changed = floodFill(bmp, bx, by, selectedColor)
            if (changed > 0) {
                filledPixels += changed
                notifyProgress()
                invalidate()
                val vibrator = context.getSystemService<Vibrator>()
                if (vibrator?.hasVibrator() == true) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        vibrator.vibrate(VibrationEffect.createOneShot(25, VibrationEffect.DEFAULT_AMPLITUDE))
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator.vibrate(25)
                    }
                }
            }
        }
    }

    private fun notifyProgress() {
        onProgressChanged?.invoke(filledPixels, totalFillablePixels)
    }

    private fun countFillablePixels(bitmap: Bitmap): Int {
        var count = 0
        val w = bitmap.width
        val h = bitmap.height
        for (y in 0 until h) {
            for (x in 0 until w) {
                if (isFillable(bitmap.getPixel(x, y))) count++
            }
        }
        return count
    }

    /**
     * Bir pikselin arka plan (boyanmamış) olup olmadığını döndürür.
     */
    private fun isBackgroundColor(color: Int): Boolean {
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        return r + g + b > 720
    }

    private fun countFilledPixels(bitmap: Bitmap): Int {
        var count = 0
        val w = bitmap.width
        val h = bitmap.height
        for (y in 0 until h) {
            for (x in 0 until w) {
                val c = bitmap.getPixel(x, y)
                // Ne hat ne de beyaz arka plan -> boyanmış sayılır
                if (!isLineColor(c) && !isBackgroundColor(c)) count++
            }
        }
        return count
    }

    /**
     * Bir pikselin hat (kontur) olup olmadığını döndürür.
     * Line-art'ta hatlar siyahtır; telefonda anti-aliasing nedeniyle
     * koyu gri tonlar da hat olarak kabul edilir.
     */
    private fun isLineColor(color: Int): Boolean {
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        return r + g + b < 360
    }

    /**
     * Bir pikselin boyanabilir olup olmadığını döndürür.
     * Hatların dışındaki açık ve orta tonlar boyanabilir kabul edilir;
     * böylece kapanmayan ince hatlar veya anti-aliased kenarlarda
     * küçük ton farkları boyamayı engellemez.
     */
    private fun isFillable(color: Int): Boolean {
        return !isLineColor(color)
    }

    /**
     * İki renk arasındaki Manhattan mesafesini döndürür.
     */
    private fun colorDistance(c1: Int, c2: Int): Int {
        return abs(Color.red(c1) - Color.red(c2)) +
                abs(Color.green(c1) - Color.green(c2)) +
                abs(Color.blue(c1) - Color.blue(c2))
    }

    /**
     * Dokunulan noktaya en yakın boyanabilir pikseli BFS ile bulur.
     * Kullanıcı hattın hemen yanına veya üzerine dokunduğunda
     * komşu bir boş bölgeyi boyamaya başlamak için kullanılır.
     */
    private fun findNearestFillableNeighbor(bitmap: Bitmap, x: Int, y: Int): Pair<Int, Int>? {
        val w = bitmap.width
        val h = bitmap.height
        val visited = BooleanArray(w * h)
        val queue = ArrayDeque<Pair<Int, Int>>()
        queue.add(x to y)
        visited[y * w + x] = true

        while (queue.isNotEmpty()) {
            val (cx, cy) = queue.removeFirst()
            if (isFillable(bitmap.getPixel(cx, cy))) return cx to cy

            for (dx in -1..1) {
                for (dy in -1..1) {
                    if (dx == 0 && dy == 0) continue
                    val nx = cx + dx
                    val ny = cy + dy
                    val idx = ny * w + nx
                    if (nx in 0 until w && ny in 0 until h && !visited[idx]) {
                        visited[idx] = true
                        queue.add(nx to ny)
                    }
                }
            }
        }
        return null
    }

    /**
     * Toleranslı flood-fill.
     * - Hedef rengine yakın pikselleri boyar (anti-aliasing/parçalanmış hat toleransı).
     - Hat piksellerinin üzerine çıkmaz.
     - Dokunulan nokta hat üzerindeyse en yakın boyanabilir komşudan başlar.
     */
    private fun floodFill(bitmap: Bitmap, x: Int, y: Int, fillColor: Int): Int {
        val w = bitmap.width
        val h = bitmap.height
        if (x !in 0 until w || y !in 0 until h) return 0

        val touchedColor = bitmap.getPixel(x, y)
        if (touchedColor == fillColor) return 0

        // Dokunulan nokta hat üzerindeyse komşu bir boş bölge bul
        var startX = x
        var startY = y
        if (isLineColor(touchedColor)) {
            val neighbor = findNearestFillableNeighbor(bitmap, x, y) ?: return 0
            startX = neighbor.first
            startY = neighbor.second
        }

        val targetColor = bitmap.getPixel(startX, startY)
        if (targetColor == fillColor) return 0

        // Tolerans: hedef renkten çok uzaksa veya hat ise boyama
        val tolerance = 140  // 0-765 arası; açık ton farklarını tolere eder

        val queue = ArrayDeque<Pair<Int, Int>>()
        queue.add(startX to startY)
        var changed = 0

        while (queue.isNotEmpty()) {
            val (cx, cy) = queue.removeFirst()
            if (cx < 0 || cx >= w || cy < 0 || cy >= h) continue

            val pixel = bitmap.getPixel(cx, cy)
            if (isLineColor(pixel)) continue
            if (colorDistance(pixel, targetColor) > tolerance) continue

            bitmap.setPixel(cx, cy, fillColor)
            changed++

            queue.add(cx + 1 to cy)
            queue.add(cx - 1 to cy)
            queue.add(cx to cy + 1)
            queue.add(cx to cy - 1)
        }
        return changed
    }
}
