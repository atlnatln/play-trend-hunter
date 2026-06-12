package com.akn.digitalcompass

import android.content.Context
import android.content.SharedPreferences

class CompassThemeManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var currentTheme: CompassTheme
        get() {
            val name = prefs.getString(KEY_THEME, CompassTheme.FLAT.name)
            return try {
                CompassTheme.valueOf(name!!)
            } catch (_: Exception) {
                CompassTheme.FLAT
            }
        }
        set(value) {
            prefs.edit().putString(KEY_THEME, value.name).apply()
        }

    fun toggle(): CompassTheme {
        val next = when (currentTheme) {
            CompassTheme.FLAT -> CompassTheme.CLASSIC_3D
            CompassTheme.CLASSIC_3D -> CompassTheme.FLAT
        }
        currentTheme = next
        return next
    }

    companion object {
        private const val PREFS_NAME = "compass_prefs"
        private const val KEY_THEME = "theme"
    }
}
