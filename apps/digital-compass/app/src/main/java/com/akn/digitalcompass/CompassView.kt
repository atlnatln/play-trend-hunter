package com.akn.digitalcompass

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import kotlin.math.*

class CompassView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var theme: CompassTheme = CompassTheme.FLAT
        set(value) {
            field = value
            invalidate()
        }

    private var azimuth = 0f
    private var pitch = 0f
    private var roll = 0f

    private val camera = Camera().apply {
        setLocation(0f, 0f, -10f)
    }
    private val matrix3D = Matrix()

    private val dp = resources.displayMetrics.density

    private val flatDirectionLabels = listOf(
        context.getString(R.string.direction_n),
        context.getString(R.string.direction_e),
        context.getString(R.string.direction_s),
        context.getString(R.string.direction_w)
    )
    private val directionLabels3D = listOf(
        context.getString(R.string.direction_n),
        context.getString(R.string.direction_ne),
        context.getString(R.string.direction_e),
        context.getString(R.string.direction_se),
        context.getString(R.string.direction_s),
        context.getString(R.string.direction_sw),
        context.getString(R.string.direction_w),
        context.getString(R.string.direction_nw)
    )

    // ---- Paints (Flat) ----
    private val flatOuterPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF03DAC5")
        style = Paint.Style.STROKE
        strokeWidth = 3f * dp
    }
    private val flatTickPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#80FFFFFF")
        style = Paint.Style.STROKE
        strokeWidth = 1.5f * dp
    }
    private val flatNeedleNorthPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF03DAC5")
        style = Paint.Style.FILL
    }
    private val flatNeedleSouthPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#40FFFFFF")
        style = Paint.Style.FILL
    }
    private val flatTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        textAlign = Paint.Align.CENTER
        typeface = Typeface.DEFAULT_BOLD
    }
    private val flatSubTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#B0FFFFFF")
        textAlign = Paint.Align.CENTER
    }

    // ---- Paints (3D) ----
    private val shadowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#40000000")
        maskFilter = BlurMaskFilter(16f * dp, BlurMaskFilter.Blur.NORMAL)
    }
    private val goldOuterPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 6f * dp
    }
    private val goldInnerPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF2A1A0A")
        style = Paint.Style.FILL
    }
    private val metalRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFD4AF37")
        style = Paint.Style.STROKE
        strokeWidth = 2f * dp
    }
    private val tick3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#CCFFFFFF")
        style = Paint.Style.STROKE
        strokeWidth = 1.2f * dp
    }
    private val tickMajor3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFFFFFFF")
        style = Paint.Style.STROKE
        strokeWidth = 2f * dp
    }
    private val needleNorth3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFE53935")
        style = Paint.Style.FILL
    }
    private val needleSouth3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFE0E0E0")
        style = Paint.Style.FILL
    }
    private val needleOutlinePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF1A0A00")
        style = Paint.Style.STROKE
        strokeWidth = 1f * dp
    }
    private val text3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        textAlign = Paint.Align.CENTER
        typeface = Typeface.DEFAULT_BOLD
    }
    private val textNorth3DPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFE53935")
        textAlign = Paint.Align.CENTER
        typeface = Typeface.DEFAULT_BOLD
    }
    private val centerCapPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFD4AF37")
        style = Paint.Style.FILL
    }
    private val centerCapOutlinePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF8B6914")
        style = Paint.Style.STROKE
        strokeWidth = 1.5f * dp
    }
    private val glassHighlightPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#20FFFFFF")
        style = Paint.Style.FILL
    }

    // ---- Bubble Level Paints ----
    private val bubblePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }
    private val bubbleShinePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#A0FFFFFF")
        style = Paint.Style.FILL
    }
    private val bubbleRingPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#18FFFFFF")
        style = Paint.Style.STROKE
        strokeWidth = 1.2f * dp
    }

    fun setOrientation(azimuth: Float, pitch: Float, roll: Float) {
        this.azimuth = azimuth
        this.pitch = pitch
        this.roll = roll
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cx = width / 2f
        val compassTop = height * 0.04f
        val compassRadius = min(width, height) * 0.38f
        val compassCy = compassTop + compassRadius

        // ---- Compass face with optional 3D tilt ----
        canvas.save()
        if (theme == CompassTheme.CLASSIC_3D) {
            camera.save()
            camera.rotateX(pitch * 0.6f)
            camera.rotateY(-roll * 0.6f)
            camera.getMatrix(matrix3D)
            camera.restore()
            matrix3D.preTranslate(-cx, -compassCy)
            matrix3D.postTranslate(cx, compassCy)
            canvas.concat(matrix3D)
        }

        if (theme == CompassTheme.CLASSIC_3D) {
            drawCompass3D(canvas, cx, compassCy, compassRadius)
        } else {
            drawCompassFlat(canvas, cx, compassCy, compassRadius)
        }

        // Bubble level draws inside the same 3D transform
        drawBubbleInsideCompass(canvas, cx, compassCy, compassRadius * 0.82f)

        canvas.restore()
    }

    // ==================== FLAT COMPASS ====================
    private fun drawCompassFlat(canvas: Canvas, cx: Float, cy: Float, r: Float) {
        canvas.drawCircle(cx, cy, r, flatOuterPaint)
        canvas.drawCircle(cx, cy, r - 4f * dp, Paint(flatOuterPaint).apply { alpha = 60 })

        canvas.save()
        canvas.rotate(-azimuth, cx, cy)

        for (deg in 0 until 360 step 15) {
            val isMajor = deg % 45 == 0
            val innerR = r - (if (isMajor) 18f else 10f) * dp
            val rad = Math.toRadians(deg.toDouble())
            val x1 = cx + r * cos(rad).toFloat()
            val y1 = cy + r * sin(rad).toFloat()
            val x2 = cx + innerR * cos(rad).toFloat()
            val y2 = cy + innerR * sin(rad).toFloat()
            canvas.drawLine(x1, y1, x2, y2, if (isMajor) flatOuterPaint else flatTickPaint)
        }

        flatTextPaint.textSize = 22f * dp
        flatSubTextPaint.textSize = 14f * dp
        val dirAngles = listOf(270, 0, 90, 180)
        for (i in flatDirectionLabels.indices) {
            val rad = Math.toRadians(dirAngles[i].toDouble())
            val tx = cx + (r - 32f * dp) * cos(rad).toFloat()
            val ty = cy + (r - 32f * dp) * sin(rad).toFloat()
            val paint = if (i == 0) flatTextPaint else flatSubTextPaint
            canvas.drawText(flatDirectionLabels[i], tx, ty + paint.textSize * 0.35f, paint)
        }

        canvas.restore()
        drawNeedleFlat(canvas, cx, cy, r * 0.75f)
    }

    private fun drawNeedleFlat(canvas: Canvas, cx: Float, cy: Float, length: Float) {
        val path = Path()
        val w = 6f * dp
        path.moveTo(cx, cy - length)
        path.lineTo(cx + w, cy)
        path.lineTo(cx - w, cy)
        path.close()
        canvas.drawPath(path, flatNeedleNorthPaint)

        val pathS = Path()
        pathS.moveTo(cx, cy + length * 0.5f)
        pathS.lineTo(cx + w, cy)
        pathS.lineTo(cx - w, cy)
        pathS.close()
        canvas.drawPath(pathS, flatNeedleSouthPaint)

        canvas.drawCircle(cx, cy, 5f * dp, flatNeedleNorthPaint)
    }

    // ==================== 3D COMPASS ====================
    private fun drawCompass3D(canvas: Canvas, cx: Float, cy: Float, r: Float) {
        canvas.drawCircle(cx + 6f * dp, cy + 8f * dp, r, shadowPaint)

        val goldGrad = LinearGradient(
            cx - r, cy - r, cx + r, cy + r,
            intArrayOf(
                Color.parseColor("#FFF5E6B3"),
                Color.parseColor("#FFD4AF37"),
                Color.parseColor("#FF8B6914"),
                Color.parseColor("#FFD4AF37"),
                Color.parseColor("#FFF5E6B3")
            ),
            floatArrayOf(0f, 0.25f, 0.5f, 0.75f, 1f),
            Shader.TileMode.CLAMP
        )
        goldOuterPaint.shader = goldGrad
        canvas.drawCircle(cx, cy, r, goldOuterPaint)
        canvas.drawCircle(cx, cy, r - 1f * dp, metalRimPaint)

        val innerR = r - 6f * dp
        canvas.drawCircle(cx, cy, innerR, goldInnerPaint)
        canvas.drawCircle(cx, cy, innerR - 2f * dp, Paint(metalRimPaint).apply { alpha = 100 })

        canvas.save()
        canvas.rotate(-azimuth, cx, cy)

        for (deg in 0 until 360 step 5) {
            val isMajor = deg % 30 == 0
            val isMinor = deg % 15 == 0
            val tickLen = when {
                isMajor -> 14f
                isMinor -> 8f
                else -> 4f
            } * dp
            val rad = Math.toRadians(deg.toDouble())
            val paint = if (isMajor) tickMajor3DPaint else tick3DPaint
            canvas.drawLine(
                cx + innerR * cos(rad).toFloat(), cy + innerR * sin(rad).toFloat(),
                cx + (innerR - tickLen) * cos(rad).toFloat(), cy + (innerR - tickLen) * sin(rad).toFloat(),
                paint
            )
        }

        text3DPaint.textSize = 24f * dp
        textNorth3DPaint.textSize = 26f * dp
        val dirAngles = listOf(270, 315, 0, 45, 90, 135, 180, 225)
        for (i in directionLabels3D.indices) {
            val rad = Math.toRadians(dirAngles[i].toDouble())
            val dist = innerR - 26f * dp
            val tx = cx + dist * cos(rad).toFloat()
            val ty = cy + dist * sin(rad).toFloat()
            val paint = if (i == 0) textNorth3DPaint else text3DPaint
            canvas.drawText(directionLabels3D[i], tx, ty + paint.textSize * 0.35f, paint)
        }

        canvas.restore()
        drawNeedle3D(canvas, cx, cy, innerR * 0.72f)

        val highlightPath = Path()
        highlightPath.addArc(
            RectF(cx - innerR + 8f * dp, cy - innerR + 8f * dp, cx + innerR - 8f * dp, cy + innerR - 8f * dp),
            200f, 100f
        )
        canvas.drawPath(highlightPath, glassHighlightPaint)

        canvas.drawCircle(cx, cy, 10f * dp, centerCapPaint)
        canvas.drawCircle(cx, cy, 10f * dp, centerCapOutlinePaint)
        canvas.drawCircle(cx - 2f * dp, cy - 2f * dp, 3f * dp, bubbleShinePaint)
    }

    private fun drawNeedle3D(canvas: Canvas, cx: Float, cy: Float, length: Float) {
        val w = 8f * dp
        val shadowOffset = 3f * dp

        val shadowPath = Path()
        shadowPath.moveTo(cx + shadowOffset, cy - length + shadowOffset)
        shadowPath.lineTo(cx + w + shadowOffset, cy + shadowOffset)
        shadowPath.lineTo(cx - w + shadowOffset, cy + shadowOffset)
        shadowPath.close()
        canvas.drawPath(shadowPath, shadowPaint)

        val northPath = Path()
        northPath.moveTo(cx, cy - length)
        northPath.lineTo(cx + w, cy)
        northPath.lineTo(cx - w, cy)
        northPath.close()
        canvas.drawPath(northPath, needleNorth3DPaint)
        canvas.drawPath(northPath, needleOutlinePaint)

        val southPath = Path()
        southPath.moveTo(cx, cy + length * 0.55f)
        southPath.lineTo(cx + w * 0.8f, cy)
        southPath.lineTo(cx - w * 0.8f, cy)
        southPath.close()
        canvas.drawPath(southPath, needleSouth3DPaint)
        canvas.drawPath(southPath, needleOutlinePaint)

        val shinePath = Path()
        shinePath.moveTo(cx, cy - length)
        shinePath.lineTo(cx + w * 0.4f, cy - length * 0.4f)
        shinePath.lineTo(cx, cy - length * 0.3f)
        shinePath.close()
        canvas.drawPath(shinePath, bubbleShinePaint)
    }

    // ==================== BUBBLE INSIDE COMPASS ====================
    private fun drawBubbleInsideCompass(canvas: Canvas, cx: Float, cy: Float, maxRadius: Float) {
        val bubbleR = 10f * dp
        val padding = 8f * dp
        val limit = maxRadius - bubbleR - padding

        // Convert tilt to bubble offset (clamp to ±25 degrees for full range)
        val maxTilt = 25f
        var bx = cx + (roll / maxTilt).coerceIn(-1f, 1f) * limit
        var by = cy + (pitch / maxTilt).coerceIn(-1f, 1f) * limit

        // Clamp to circle boundary
        val dx = bx - cx
        val dy = by - cy
        val dist = hypot(dx, dy)
        if (dist > limit && dist > 0) {
            bx = cx + dx * (limit / dist)
            by = cy + dy * (limit / dist)
        }

        val normalizedDist = (dist / limit).coerceIn(0f, 1f)
        val bubbleColor = when {
            normalizedDist < 0.25f -> Color.parseColor("#FF4CAF50")
            normalizedDist < 0.55f -> Color.parseColor("#FFFFC107")
            else -> Color.parseColor("#FFE53935")
        }
        bubblePaint.color = bubbleColor

        // Subtle ring where bubble moves
        canvas.drawCircle(cx, cy, limit + bubbleR, bubbleRingPaint)

        // Bubble shadow
        canvas.drawCircle(bx + 1.5f * dp, by + 2f * dp, bubbleR, Paint(shadowPaint).apply { alpha = 100 })

        // Bubble
        canvas.drawCircle(bx, by, bubbleR, bubblePaint)

        // Shine
        canvas.drawCircle(bx - 3f * dp, by - 3f * dp, 3.5f * dp, bubbleShinePaint)
    }
}
