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

    private fun countFilledPixels(bitmap: Bitmap): Int {
        var count = 0
        val w = bitmap.width
        val h = bitmap.height
        for (y in 0 until h) {
            for (x in 0 until w) {
                val c = bitmap.getPixel(x, y)
                if (!isFillable(c) && !isLineColor(c)) count++
            }
        }
        return count
    }

    private fun isLineColor(color: Int): Boolean {
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        return r + g + b < 180
    }

    private fun isFillable(color: Int): Boolean {
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        return r + g + b > 600
    }

    private fun floodFill(bitmap: Bitmap, x: Int, y: Int, fillColor: Int): Int {
        val targetColor = bitmap.getPixel(x, y)
        if (targetColor == fillColor) return 0
        if (!isFillable(targetColor)) return 0

        val w = bitmap.width
        val h = bitmap.height
        val queue = ArrayDeque<Pair<Int, Int>>()
        queue.add(x to y)
        var changed = 0

        while (queue.isNotEmpty()) {
            val (cx, cy) = queue.removeFirst()
            if (cx < 0 || cx >= w || cy < 0 || cy >= h) continue
            if (bitmap.getPixel(cx, cy) != targetColor) continue
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
