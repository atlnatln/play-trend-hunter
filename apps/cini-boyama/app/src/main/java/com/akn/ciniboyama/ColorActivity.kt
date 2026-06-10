package com.akn.ciniboyama

import android.os.Bundle
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.materialswitch.MaterialSwitch

class ColorActivity : AppCompatActivity() {

    private val colors by lazy {
        listOf(
            0xFF1E3A8A.toInt(), // Kobalt Mavi
            0xFF0EA5E9.toInt(), // Turkuaz
            0xFF047857.toInt(), // Yeşil
            0xFFB91C1C.toInt(), // Kırmızı
            0xFFF59E0B.toInt(), // Sarı
            0xFFFEF3C7.toInt(), // Krem
            0xFFFFFFFF.toInt(), // Beyaz
            0xFF111827.toInt(), // Siyah
            0xFF7C3AED.toInt(), // Mor
            0xFFEC4899.toInt(), // Pembe
            0xFF92400E.toInt(), // Kahve
            0xFFD4AF37.toInt(), // Altın
        )
    }

    private lateinit var coloringView: ColoringView
    private lateinit var progressText: TextView
    private lateinit var colorAdapter: ColorAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_color)

        val lineartRes = intent.getIntExtra(MainActivity.EXTRA_LINEART, -1)
        val title = intent.getStringExtra(MainActivity.EXTRA_TITLE) ?: ""

        findViewById<MaterialToolbar>(R.id.toolbar).apply {
            this.title = title
            setNavigationOnClickListener { finish() }
        }

        progressText = findViewById(R.id.progress_text)
        val progressBar = findViewById<ProgressBar>(R.id.progress_bar)

        coloringView = findViewById(R.id.coloring_view)
        coloringView.onProgressChanged = { filled, total ->
            val percent = if (total > 0) (filled * 100 / total).coerceIn(0, 100) else 0
            progressText.text = getString(R.string.progress_format, percent)
            progressBar.progress = percent
        }

        val colorRecycler = findViewById<RecyclerView>(R.id.color_recycler)
        colorRecycler.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        colorAdapter = ColorAdapter(colors) { color ->
            coloringView.selectedColor = color
        }
        colorRecycler.adapter = colorAdapter
        coloringView.selectedColor = colorAdapter.getSelectedColor()

        coloringView.setPattern(lineartRes)

        findViewById<MaterialSwitch>(R.id.glaze_switch).setOnCheckedChangeListener { _, isChecked ->
            coloringView.setGlazeEnabled(isChecked)
        }

        findViewById<MaterialButton>(R.id.clear_button).setOnClickListener {
            coloringView.reset()
        }
    }
}
