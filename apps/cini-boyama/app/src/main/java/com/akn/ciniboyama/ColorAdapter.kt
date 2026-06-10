package com.akn.ciniboyama

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton

class ColorAdapter(
    private val colors: List<Int>,
    private val onColorSelected: (Int) -> Unit
) : RecyclerView.Adapter<ColorAdapter.VH>() {

    private var selectedPosition = 0

    inner class VH(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val button: MaterialButton = itemView.findViewById(R.id.color_button)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_color, parent, false)
        return VH(view)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val color = colors[position]
        val btn = holder.button
        btn.setBackgroundColor(color)
        val isSelected = position == selectedPosition
        btn.strokeWidth = if (isSelected) 8 else 3
        btn.strokeColor = android.content.res.ColorStateList.valueOf(
            if (isSelected) 0xFFFFFFFF.toInt() else 0xFF666666.toInt()
        )
        btn.setOnClickListener {
            val prev = selectedPosition
            selectedPosition = holder.adapterPosition
            notifyItemChanged(prev)
            notifyItemChanged(selectedPosition)
            onColorSelected(color)
        }
    }

    override fun getItemCount(): Int = colors.size

    fun getSelectedColor(): Int = colors.getOrElse(selectedPosition) { colors.first() }
}
