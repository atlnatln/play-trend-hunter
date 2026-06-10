package com.akn.ciniboyama

import androidx.annotation.DrawableRes

data class Pattern(
    @DrawableRes val previewRes: Int,
    @DrawableRes val lineartRes: Int,
    val title: String
)
