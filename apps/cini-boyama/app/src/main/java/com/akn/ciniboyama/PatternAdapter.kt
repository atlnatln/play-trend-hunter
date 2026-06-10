package com.akn.ciniboyama

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class PatternAdapter(
    private val patterns: List<Pattern>,
    private val onClick: (Pattern) -> Unit
) : RecyclerView.Adapter<PatternAdapter.VH>() {

    inner class VH(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val image: ImageView = itemView.findViewById(R.id.pattern_image)
        val title: TextView = itemView.findViewById(R.id.pattern_title)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_pattern, parent, false)
        return VH(view)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val pattern = patterns[position]
        holder.image.setImageResource(pattern.previewRes)
        holder.title.text = pattern.title
        holder.itemView.setOnClickListener { onClick(pattern) }
    }

    override fun getItemCount(): Int = patterns.size
}
