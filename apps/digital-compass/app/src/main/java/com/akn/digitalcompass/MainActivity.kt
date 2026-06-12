package com.akn.digitalcompass

import android.Manifest
import android.content.pm.PackageManager
import android.hardware.GeomagneticField
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.Looper
import android.graphics.Color
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.akn.digitalcompass.databinding.ActivityMainBinding
import kotlin.math.atan2
import kotlin.math.sqrt

class MainActivity : AppCompatActivity(), SensorEventListener, LocationListener {

    private lateinit var binding: ActivityMainBinding
    private lateinit var sensorManager: SensorManager
    private lateinit var themeManager: CompassThemeManager
    private lateinit var locationManager: LocationManager

    private var accelerometer: Sensor? = null
    private var magnetometer: Sensor? = null

    private val accelReading = FloatArray(3)
    private val magnetReading = FloatArray(3)
    private val rotationMatrix = FloatArray(9)
    private val orientationAngles = FloatArray(3)

    private var lastUpdate = 0L
    private val updateIntervalMs = 80L

    private var magnetAccuracy = SensorManager.SENSOR_STATUS_UNRELIABLE
    private var accelAccuracy = SensorManager.SENSOR_STATUS_UNRELIABLE
    private var hasGpsFix = false

    private var currentLat = 0.0
    private var currentLon = 0.0
    private var currentAlt = 0.0
    private var declination = 0f
    private var useTrueNorth = false

    private var isCalibrating = false
    private var calibrateProgress = 0

    companion object {
        private const val LOCATION_PERMISSION_REQUEST = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        themeManager = CompassThemeManager(this)
        binding.compassView.theme = themeManager.currentTheme
        updateThemeButton()

        binding.btnTheme.setOnClickListener {
            val newTheme = themeManager.toggle()
            binding.compassView.theme = newTheme
            updateThemeButton()
        }
        binding.btnHelp.setOnClickListener { showHelpDialog() }

        binding.btnCalibrate.setOnClickListener { startCalibration() }
        binding.btnCalibrateDone.setOnClickListener { stopCalibration() }

        binding.switchTrueNorth.setOnCheckedChangeListener { _, checked ->
            useTrueNorth = checked
        }

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        magnetometer = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)

        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        requestLocationIfNeeded()
        updateSensorIndicators()
    }

    private fun updateThemeButton() {
        binding.btnTheme.text = when (themeManager.currentTheme) {
            CompassTheme.FLAT -> getString(R.string.theme_2d)
            CompassTheme.CLASSIC_3D -> getString(R.string.theme_3d)
        }
    }

    // ---- Calibration ----
    private fun startCalibration() {
        isCalibrating = true
        calibrateProgress = 0
        binding.calibrationOverlay.visibility = View.VISIBLE
        updateCalibrationProgress()
    }

    private fun stopCalibration() {
        isCalibrating = false
        binding.calibrationOverlay.visibility = View.GONE
    }

    private fun updateCalibrationProgress() {
        val pb = binding.calibrationOverlay.findViewById<ProgressBar>(R.id.calibrate_progress)
        val status = binding.calibrationOverlay.findViewById<TextView>(R.id.tv_calibrate_status)

        val progress = when (magnetAccuracy) {
            SensorManager.SENSOR_STATUS_ACCURACY_HIGH -> 100
            SensorManager.SENSOR_STATUS_ACCURACY_MEDIUM -> 60
            SensorManager.SENSOR_STATUS_ACCURACY_LOW -> 25
            else -> 0
        }
        pb?.progress = progress

        val (text, color) = when (magnetAccuracy) {
            SensorManager.SENSOR_STATUS_ACCURACY_HIGH ->
                getString(R.string.calibrate_ok) to Color.parseColor("#FF4CAF50")
            SensorManager.SENSOR_STATUS_ACCURACY_MEDIUM ->
                getString(R.string.accuracy_medium) to Color.parseColor("#FFFFC107")
            else ->
                getString(R.string.accuracy_low) to Color.parseColor("#FFE53935")
        }
        status?.text = text
        status?.setTextColor(color)
    }

    // ---- Location ----
    private fun requestLocationIfNeeded() {
        when {
            ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                    == PackageManager.PERMISSION_GRANTED -> {
                startLocationUpdates()
            }
            else -> {
                binding.tvCoords.text = getString(R.string.coords_unavailable)
                binding.tvAltitude.text = getString(R.string.altitude_na)
                ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
                    LOCATION_PERMISSION_REQUEST)
            }
        }
    }

    private fun startLocationUpdates() {
        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                2000L, 5f, this, Looper.getMainLooper()
            )
            locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let {
                onLocationChanged(it)
            }
        } catch (_: SecurityException) {
            binding.tvCoords.text = getString(R.string.coords_unavailable)
            binding.tvAltitude.text = getString(R.string.altitude_na)
        }
    }

    override fun onLocationChanged(location: Location) {
        currentLat = location.latitude
        currentLon = location.longitude
        currentAlt = location.altitude
        hasGpsFix = true

        binding.tvCoords.text = getString(R.string.coords_format, currentLat, currentLon)
        binding.tvAltitude.text = getString(R.string.altitude, currentAlt.toInt())

        val geoField = GeomagneticField(
            currentLat.toFloat(), currentLon.toFloat(), currentAlt.toFloat(),
            System.currentTimeMillis()
        )
        declination = geoField.declination

        updateSensorIndicators()
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_PERMISSION_REQUEST &&
            grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED
        ) {
            startLocationUpdates()
        } else {
            binding.tvCoords.text = getString(R.string.coords_unavailable)
            binding.tvAltitude.text = getString(R.string.altitude_na)
            updateSensorIndicators()
        }
    }

    // ---- Sensors ----
    override fun onResume() {
        super.onResume()
        accelerometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_UI) }
        magnetometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_UI) }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {
            startLocationUpdates()
        }
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
        try {
            locationManager.removeUpdates(this)
        } catch (_: SecurityException) {}
    }

    override fun onSensorChanged(event: SensorEvent) {
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                System.arraycopy(event.values, 0, accelReading, 0, 3)
            }
            Sensor.TYPE_MAGNETIC_FIELD -> {
                System.arraycopy(event.values, 0, magnetReading, 0, 3)
                updateMagneticField()
            }
        }

        val now = System.currentTimeMillis()
        if (now - lastUpdate < updateIntervalMs) return
        lastUpdate = now

        var magneticAzimuth = 0f
        if (SensorManager.getRotationMatrix(rotationMatrix, null, accelReading, magnetReading)) {
            SensorManager.getOrientation(rotationMatrix, orientationAngles)
            magneticAzimuth = Math.toDegrees(orientationAngles[0].toDouble()).toFloat()
        }

        val azimuth = if (useTrueNorth) {
            ((magneticAzimuth + declination + 360) % 360)
        } else {
            ((magneticAzimuth + 360) % 360)
        }
        val degrees = azimuth.toInt()

        val ax = accelReading[0]
        val ay = accelReading[1]
        val az = accelReading[2]

        val pitch = Math.toDegrees(atan2(ay.toDouble(), sqrt((ax * ax + az * az).toDouble()))).toFloat()
        val roll = Math.toDegrees(atan2((-ax).toDouble(), az.toDouble())).toFloat()

        runOnUiThread {
            binding.tvDegrees.text = getString(R.string.compass_degrees, degrees)
            binding.tvDirection.text = directionName(degrees)
            binding.compassView.setOrientation(azimuth, pitch, roll)
        }
    }

    private fun updateMagneticField() {
        val mx = magnetReading[0]
        val my = magnetReading[1]
        val mz = magnetReading[2]
        val microTesla = sqrt(mx * mx + my * my + mz * mz)
        runOnUiThread {
            binding.tvMagneticField.text = getString(R.string.magnetic_field, microTesla)
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        when (sensor?.type) {
            Sensor.TYPE_MAGNETIC_FIELD -> magnetAccuracy = accuracy
            Sensor.TYPE_ACCELEROMETER -> accelAccuracy = accuracy
        }
        runOnUiThread {
            updateSensorIndicators()
            if (isCalibrating) updateCalibrationProgress()
        }
    }

    private fun updateSensorIndicators() {
        val magColor = when (magnetAccuracy) {
            SensorManager.SENSOR_STATUS_ACCURACY_HIGH -> Color.parseColor("#FF4CAF50")
            SensorManager.SENSOR_STATUS_ACCURACY_MEDIUM -> Color.parseColor("#FFFFC107")
            else -> Color.parseColor("#FFE53935")
        }
        binding.tvSensorMag.setTextColor(magColor)

        val accColor = when (accelAccuracy) {
            SensorManager.SENSOR_STATUS_ACCURACY_HIGH -> Color.parseColor("#FF4CAF50")
            SensorManager.SENSOR_STATUS_ACCURACY_MEDIUM -> Color.parseColor("#FFFFC107")
            else -> Color.parseColor("#FFE53935")
        }
        binding.tvSensorAcc.setTextColor(accColor)

        val gpsColor = if (hasGpsFix) Color.parseColor("#FF4CAF50") else Color.parseColor("#FFE53935")
        binding.tvSensorGps.setTextColor(gpsColor)

        // Show calibration banner if magnetometer accuracy is low
        if (magnetAccuracy <= SensorManager.SENSOR_STATUS_ACCURACY_LOW) {
            binding.tvCalibrateBanner.visibility = View.VISIBLE
        } else {
            binding.tvCalibrateBanner.visibility = View.GONE
        }
    }

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

    private fun showHelpDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_help, null)
        AlertDialog.Builder(this)
            .setTitle(getString(R.string.help_title))
            .setView(dialogView)
            .setPositiveButton(getString(R.string.help_close)) { dialog, _ -> dialog.dismiss() }
            .create()
            .show()
    }
}
