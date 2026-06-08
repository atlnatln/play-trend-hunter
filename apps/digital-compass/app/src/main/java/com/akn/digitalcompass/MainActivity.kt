package com.akn.digitalcompass

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.os.Looper
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.os.postDelayed

class MainActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null
    private var magnetometer: Sensor? = null

    private val accelReading = FloatArray(3)
    private val magnetReading = FloatArray(3)
    private val rotationMatrix = FloatArray(9)
    private val orientationAngles = FloatArray(3)

    private var lastUpdate = 0L
    private val updateIntervalMs = 100L

    private lateinit var tvDegrees: TextView
    private lateinit var tvDirection: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvDegrees = findViewById(R.id.tv_degrees)
        tvDirection = findViewById(R.id.tv_direction)

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        magnetometer = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)
    }

    override fun onResume() {
        super.onResume()
        accelerometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_UI) }
        magnetometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_UI) }
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                System.arraycopy(event.values, 0, accelReading, 0, 3)
            }
            Sensor.TYPE_MAGNETIC_FIELD -> {
                System.arraycopy(event.values, 0, magnetReading, 0, 3)
            }
        }

        val now = System.currentTimeMillis()
        if (now - lastUpdate < updateIntervalMs) return
        lastUpdate = now

        if (SensorManager.getRotationMatrix(rotationMatrix, null, accelReading, magnetReading)) {
            SensorManager.getOrientation(rotationMatrix, orientationAngles)
            val azimuth = Math.toDegrees(orientationAngles[0].toDouble()).toFloat()
            val degrees = ((azimuth + 360) % 360).toInt()

            android.os.Handler(Looper.getMainLooper()).post {
                tvDegrees.text = getString(R.string.compass_degrees, degrees)
                tvDirection.text = directionName(degrees)
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun directionName(degrees: Int): String {
        return when (degrees) {
            in 338..360, in 0..22 -> getString(R.string.direction_n)
            in 23..67 -> getString(R.string.direction_ne)
            in 68..112 -> getString(R.string.direction_e)
            in 113..157 -> getString(R.string.direction_se)
            in 158..202 -> getString(R.string.direction_s)
            in 203..247 -> getString(R.string.direction_sw)
            in 248..292 -> getString(R.string.direction_w)
            in 293..337 -> getString(R.string.direction_nw)
            else -> getString(R.string.direction_n)
        }
    }
}
