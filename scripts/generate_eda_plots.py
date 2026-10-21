#!/usr/bin/env python3
"""
PriceNest — Generate Standalone SVG Charts for Phase 2 EDA
Generates vector charts without external dependencies (pure Python standard library).
"""

import csv
import math
import os
from collections import Counter, defaultdict


def create_bar_chart(title, categories, values, filename, val_prefix="", val_suffix="", bar_color="#4F46E5"):
    width = 800
    height = 420
    margin_top = 60
    margin_bottom = 80
    margin_left = 100
    margin_right = 40

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_val = max(values) * 1.15 if values else 1.0

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#ffffff; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<text x="{width/2}" y="35" text-anchor="middle" font-size="18" font-weight="700" fill="#1F2937">{title}</text>',
    ]

    # Grid lines & Y-axis labels
    y_ticks = 5
    for i in range(y_ticks + 1):
        y_val = (max_val / y_ticks) * i
        y_pos = margin_top + plot_height - (i * (plot_height / y_ticks))
        svg.append(f'<line x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" stroke="#E5E7EB" stroke-width="1"/>')
        formatted_val = f"{y_val:,.0f}" if y_val >= 10 else f"{y_val:.2f}"
        svg.append(f'<text x="{margin_left - 12}" y="{y_pos + 4}" text-anchor="end" font-size="11" fill="#6B7280">{val_prefix}{formatted_val}{val_suffix}</text>')

    # Bars
    n = len(categories)
    bar_width = plot_width / (n * 1.5)
    gap = plot_width / n

    for i, (cat, val) in enumerate(zip(categories, values)):
        bar_height = (val / max_val) * plot_height
        x = margin_left + (i * gap) + (gap - bar_width) / 2
        y = margin_top + plot_height - bar_height

        # Highlight Pune if present
        curr_color = "#E11D48" if cat == "Pune" else bar_color

        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{curr_color}" rx="4"/>')
        label_val = f"{val:,.0f}" if val >= 10 else f"{val:.2f}"
        svg.append(f'<text x="{x + bar_width/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="#374151">{val_prefix}{label_val}{val_suffix}</text>')
        # X-axis label
        svg.append(f'<text x="{x + bar_width/2:.1f}" y="{margin_top + plot_height + 24:.1f}" text-anchor="middle" font-size="12" fill="#4B5563" transform="rotate(25 {x + bar_width/2:.1f} {margin_top + plot_height + 24:.1f})">{cat}</text>')

    # X-axis baseline
    svg.append(f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{width - margin_right}" y2="{margin_top + plot_height}" stroke="#9CA3AF" stroke-width="1.5"/>')
    svg.append('</svg>')

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated chart: {filename}")


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "pune_housing_raw.csv")
    plots_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "dataset", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 1. City Counts
    city_counts = Counter(r["City"] for r in rows)
    sorted_cities = sorted(city_counts.items(), key=lambda x: -x[1])
    create_bar_chart(
        title="Dataset Geographic Distribution (Rows per City - Total 80,000)",
        categories=[c[0] for c in sorted_cities],
        values=[c[1] for c in sorted_cities],
        filename=os.path.join(plots_dir, "city_distribution.svg"),
        val_suffix="",
        bar_color="#3B82F6",
    )

    # 2. Average Rate per SqFt by City
    city_rates = defaultdict(list)
    for r in rows:
        city_rates[r["City"]].append(float(r["Price_INR_Lakhs"]) * 100000.0 / float(r["Super_Area_SqFt"]))
    avg_city_rates = [(c, sum(vals)/len(vals)) for c, vals in city_rates.items()]
    avg_city_rates.sort(key=lambda x: -x[1])
    create_bar_chart(
        title="Mean Property Rate by City (₹ per Super Sq. Ft.)",
        categories=[c[0] for c in avg_city_rates],
        values=[round(c[1], 1) for c in avg_city_rates],
        filename=os.path.join(plots_dir, "city_rates.svg"),
        val_prefix="₹",
        bar_color="#0D9488",
    )

    # 3. Correlation with Price (Pune Subset)
    pune_rows = [r for r in rows if r["City"] == "Pune"]
    pune_prices = [float(r["Price_INR_Lakhs"]) for r in pune_rows]

    def corr(xs, ys):
        n = len(xs)
        mx = sum(xs)/n
        my = sum(ys)/n
        cov = sum((x - mx)*(y - my) for x, y in zip(xs, ys))
        vx = sum((x - mx)**2 for x in xs)
        vy = sum((y - my)**2 for y in ys)
        return cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else 0.0

    features = [
        ("Super Area", [float(r["Super_Area_SqFt"]) for r in pune_rows]),
        ("Carpet Area", [float(r["Carpet_Area_SqFt"]) for r in pune_rows]),
        ("Age of Prop", [float(r["Age_of_Property"]) for r in pune_rows]),
        ("Dist Center", [float(r["Distance_to_City_Center_km"]) for r in pune_rows]),
        ("BHK", [float(r["BHK"]) for r in pune_rows]),
        ("Bathrooms", [float(r["Bathrooms"]) for r in pune_rows]),
        ("Floor Num", [float(r["Floor_Number"]) for r in pune_rows]),
        ("Total Floors", [float(r["Total_Floors"]) for r in pune_rows]),
        ("Dist Metro", [float(r["Distance_to_Metro_km"]) for r in pune_rows]),
        ("Parking", [float(r["Parking"]) for r in pune_rows]),
    ]
    corrs = [(name, round(corr(data, pune_prices), 3)) for name, data in features]
    create_bar_chart(
        title="Pearson Correlation with Price (Pune Subset: N=7,833)",
        categories=[c[0] for c in corrs],
        values=[c[1] for c in corrs],
        filename=os.path.join(plots_dir, "feature_correlations.svg"),
        val_prefix="",
        bar_color="#6366F1",
    )

    # 4. Locality Type Distribution (Pune)
    pune_locs = Counter(r["Locality_Type"] for r in pune_rows)
    create_bar_chart(
        title="Pune Locality Type Breakdown (N=7,833)",
        categories=list(pune_locs.keys()),
        values=list(pune_locs.values()),
        filename=os.path.join(plots_dir, "pune_locality_type.svg"),
        bar_color="#F59E0B",
    )

    print("All charts successfully generated!")


if __name__ == "__main__":
    main()
