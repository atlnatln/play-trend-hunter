package com.akn.ciniboyama

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.appbar.MaterialToolbar

class MainActivity : AppCompatActivity() {

    private val patterns by lazy {
        listOf(
            Pattern(R.drawable.preview_iznik_tile, R.drawable.lineart_iznik_tile, getString(R.string.pattern_iznik_tile)),
            Pattern(R.drawable.preview_iznik_vase, R.drawable.lineart_iznik_vase, getString(R.string.pattern_iznik_vase)),
            Pattern(R.drawable.preview_geometric, R.drawable.lineart_geometric, getString(R.string.pattern_geometric)),
            Pattern(R.drawable.preview_flower, R.drawable.lineart_flower, getString(R.string.pattern_flower)),
            Pattern(R.drawable.preview_car_tile, R.drawable.lineart_car_tile, getString(R.string.pattern_car_tile)),
            Pattern(R.drawable.preview_dino_mandala, R.drawable.lineart_dino_mandala, getString(R.string.pattern_dino_mandala)),
            Pattern(R.drawable.preview_rocket_stars, R.drawable.lineart_rocket_stars, getString(R.string.pattern_rocket_stars)),
            Pattern(R.drawable.preview_soccer_mandala, R.drawable.lineart_soccer_mandala, getString(R.string.pattern_soccer_mandala)),
            Pattern(R.drawable.preview_butterfly_tile, R.drawable.lineart_butterfly_tile, getString(R.string.pattern_butterfly_tile)),
            Pattern(R.drawable.preview_unicorn_mandala, R.drawable.lineart_unicorn_mandala, getString(R.string.pattern_unicorn_mandala)),
            Pattern(R.drawable.preview_princess_crown, R.drawable.lineart_princess_crown, getString(R.string.pattern_princess_crown)),
            Pattern(R.drawable.preview_heart_mandala, R.drawable.lineart_heart_mandala, getString(R.string.pattern_heart_mandala)),
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<MaterialToolbar>(R.id.toolbar).title = getString(R.string.app_name)

        val recycler = findViewById<RecyclerView>(R.id.pattern_recycler)
        recycler.layoutManager = GridLayoutManager(this, 2)
        recycler.adapter = PatternAdapter(patterns) { pattern ->
            val intent = Intent(this, ColorActivity::class.java).apply {
                putExtra(EXTRA_LINEART, pattern.lineartRes)
                putExtra(EXTRA_TITLE, pattern.title)
            }
            startActivity(intent)
        }
    }

    companion object {
        const val EXTRA_LINEART = "lineart_res"
        const val EXTRA_TITLE = "title"
    }
}
