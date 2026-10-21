#!/usr/bin/env python3
"""
PriceNest — Dataset Profiling & Feasibility Audit Script
Phase 2.0: Non-destructive data profiling of data/raw/pune_housing_raw.csv
Standard library only (csv, math, collections, json, statistics, sys)
"""

import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
from statistics import mean, median, stdev


def percentile(data, p):
    """Calculate the p-th percentile of sorted data."""
    if not data:
        return 0.0
    k = (len(data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(data[int(k)])
    d0 = data[int(f)] * (c - k)
    d1 = data[int(c)] * (k - f)
    return float(d0 + d1)


def summarize_numeric(values):
    """Compute comprehensive descriptive statistics for numeric list."""
    if not values:
        return {}
    s_vals = sorted(values)
    n = len(s_vals)
    return {
        "count": n,
        "mean": round(mean(s_vals), 2),
        "std": round(stdev(s_vals), 2) if n > 1 else 0.0,
        "min": round(s_vals[0], 2),
        "p1": round(percentile(s_vals, 1), 2),
        "p5": round(percentile(s_vals, 5), 2),
        "p25": round(percentile(s_vals, 25), 2),
        "median": round(median(s_vals), 2),
        "p75": round(percentile(s_vals, 75), 2),
        "p95": round(percentile(s_vals, 95), 2),
        "p99": round(percentile(s_vals, 99), 2),
        "max": round(s_vals[-1], 2),
    }


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "pune_housing_raw.csv")
    csv_path = os.path.abspath(csv_path)

    if not os.path.exists(csv_path):
        print(f"ERROR: Dataset not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    file_size_bytes = os.path.getsize(csv_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    print(f"Loading {csv_path} ({file_size_mb} MB)...")

    rows = []
    headers = []
    with open(csv_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print("ERROR: CSV is empty!", file=sys.stderr)
            sys.exit(1)

        for line_num, row in enumerate(reader, start=2):
            if len(row) != len(headers):
                print(f"Warning: line {line_num} has {len(row)} columns, expected {len(headers)}")
            rows.append(row)

    total_rows = len(rows)
    total_cols = len(headers)
    print(f"Total rows: {total_rows:,}, Total columns: {total_cols}")
    print(f"Headers: {headers}")

    # Column index lookup
    col_idx = {h: i for i, h in enumerate(headers)}

    # 1. Null / Missing Values Analysis
    null_counts = Counter()
    for row in rows:
        for i, val in enumerate(row):
            v_strip = val.strip()
            if v_strip == "" or v_strip.lower() in ("null", "none", "nan", "na"):
                null_counts[headers[i]] += 1

    # 2. Duplicate Analysis
    property_ids = [row[col_idx["Property_ID"]] for row in rows if "Property_ID" in col_idx]
    unique_prop_ids = set(property_ids)
    duplicate_prop_ids = len(property_ids) - len(unique_prop_ids)

    # 3. Categorical Distributions
    cat_cols = [
        "City",
        "Locality_Type",
        "Property_Type",
        "Furnishing_Status",
        "Parking",
        "Lift_Available",
        "Gated_Community",
    ]
    cat_dists = {}
    for c in cat_cols:
        if c in col_idx:
            c_idx = col_idx[c]
            counts = Counter(row[c_idx].strip() for row in rows)
            cat_dists[c] = dict(counts.most_common())

    # 4. Numerical Parsings & Analysis
    num_cols = [
        "BHK",
        "Bathrooms",
        "Super_Area_SqFt",
        "Carpet_Area_SqFt",
        "Floor_Number",
        "Total_Floors",
        "Age_of_Property",
        "Distance_to_Metro_km",
        "Distance_to_City_Center_km",
        "Price_INR_Lakhs",
    ]

    num_data = defaultdict(list)
    parse_errors = Counter()

    for row in rows:
        for c in num_cols:
            if c in col_idx:
                raw_val = row[col_idx[c]].strip()
                try:
                    num_data[c].append(float(raw_val))
                except ValueError:
                    parse_errors[c] += 1

    num_stats = {c: summarize_numeric(num_data[c]) for c in num_cols}

    # 5. Derived Metrics (All Data vs Pune Subset)
    # Check City column
    has_city = "City" in col_idx
    city_idx = col_idx["City"] if has_city else -1

    pune_rows = [r for r in rows if r[city_idx].strip().lower() == "pune"] if has_city else []
    print(f"Pune rows count: {len(pune_rows):,} ({len(pune_rows)/total_rows*100:.2f}% of total)")

    # Derived metrics across whole dataset
    derived_sqft_per_bhk = []
    derived_carpet_ratio = []
    derived_rate_super = []
    derived_rate_carpet = []
    anomalies = {
        "floor_gt_total_floors": 0,
        "villa_high_rise": 0,  # Villa or house with Total_Floors > 4 or Floor_Number > 3
        "independent_house_high_rise": 0,
        "carpet_gt_super": 0,
        "sqft_per_bhk_lt_100": 0,
        "sqft_per_bhk_lt_150": 0,
        "bathrooms_gt_bhk_plus_2": 0,
        "negative_or_zero_price": 0,
        "negative_or_zero_area": 0,
    }

    prop_type_idx = col_idx.get("Property_Type", -1)
    floor_idx = col_idx.get("Floor_Number", -1)
    total_floor_idx = col_idx.get("Total_Floors", -1)
    bhk_idx = col_idx.get("BHK", -1)
    bath_idx = col_idx.get("Bathrooms", -1)
    super_idx = col_idx.get("Super_Area_SqFt", -1)
    carpet_idx = col_idx.get("Carpet_Area_SqFt", -1)
    price_idx = col_idx.get("Price_INR_Lakhs", -1)

    for r in rows:
        try:
            fl = float(r[floor_idx])
            tfl = float(r[total_floor_idx])
            bhk = float(r[bhk_idx])
            bath = float(r[bath_idx])
            s_area = float(r[super_idx])
            c_area = float(r[carpet_idx])
            price = float(r[price_idx])
            ptype = r[prop_type_idx].strip()

            if fl > tfl:
                anomalies["floor_gt_total_floors"] += 1
            if ptype.lower() == "villa" and (fl > 3 or tfl > 4):
                anomalies["villa_high_rise"] += 1
            if ptype.lower() == "independent house" and (fl > 3 or tfl > 4):
                anomalies["independent_house_high_rise"] += 1
            if c_area > s_area:
                anomalies["carpet_gt_super"] += 1
            if bhk > 0:
                sqft_bhk = c_area / bhk
                derived_sqft_per_bhk.append(sqft_bhk)
                if sqft_bhk < 100:
                    anomalies["sqft_per_bhk_lt_100"] += 1
                if sqft_bhk < 150:
                    anomalies["sqft_per_bhk_lt_150"] += 1
            if bath > (bhk + 2):
                anomalies["bathrooms_gt_bhk_plus_2"] += 1
            if price <= 0:
                anomalies["negative_or_zero_price"] += 1
            if s_area <= 0 or c_area <= 0:
                anomalies["negative_or_zero_area"] += 1

            if s_area > 0:
                derived_carpet_ratio.append(c_area / s_area)
                derived_rate_super.append((price * 100000.0) / s_area)
            if c_area > 0:
                derived_rate_carpet.append((price * 100000.0) / c_area)
        except (ValueError, IndexError):
            pass

    # 6. City-by-City Pricing Breakdown
    city_stats = {}
    city_prices = defaultdict(list)
    city_rates = defaultdict(list)
    city_super_areas = defaultdict(list)

    for r in rows:
        try:
            city = r[city_idx].strip()
            price = float(r[price_idx])
            s_area = float(r[super_idx])
            city_prices[city].append(price)
            if s_area > 0:
                city_rates[city].append((price * 100000.0) / s_area)
            city_super_areas[city].append(s_area)
        except (ValueError, IndexError):
            pass

    for city, prices in city_prices.items():
        city_stats[city] = {
            "record_count": len(prices),
            "pct_of_total": round(len(prices) / total_rows * 100, 2),
            "price_inr_lakhs": summarize_numeric(prices),
            "rate_per_sqft": summarize_numeric(city_rates[city]),
            "super_area_sqft": summarize_numeric(city_super_areas[city]),
        }

    # 7. Pune Deep Dive
    pune_num_data = defaultdict(list)
    for r in pune_rows:
        for c in num_cols:
            try:
                pune_num_data[c].append(float(r[col_idx[c]]))
            except ValueError:
                pass
    pune_num_stats = {c: summarize_numeric(pune_num_data[c]) for c in num_cols}

    pune_cat_dists = {}
    for c in cat_cols:
        counts = Counter(r[col_idx[c]].strip() for r in pune_rows)
        pune_cat_dists[c] = dict(counts.most_common())

    # Compile Full Audit Results
    audit_results = {
        "file_info": {
            "path": csv_path,
            "size_bytes": file_size_bytes,
            "size_mb": file_size_mb,
            "total_rows": total_rows,
            "total_columns": total_cols,
            "headers": headers,
        },
        "null_counts": dict(null_counts),
        "parse_errors": dict(parse_errors),
        "duplicates": {
            "duplicate_property_ids": duplicate_prop_ids,
            "unique_property_ids": len(unique_prop_ids),
        },
        "categorical_distributions": cat_dists,
        "numerical_statistics_all": num_stats,
        "anomalies": anomalies,
        "derived_metrics": {
            "carpet_to_super_ratio": summarize_numeric(derived_carpet_ratio),
            "sqft_per_bhk": summarize_numeric(derived_sqft_per_bhk),
            "rate_per_super_sqft": summarize_numeric(derived_rate_super),
            "rate_per_carpet_sqft": summarize_numeric(derived_rate_carpet),
        },
        "city_breakdown": city_stats,
        "pune_subset": {
            "row_count": len(pune_rows),
            "percentage_of_total": round(len(pune_rows) / total_rows * 100, 2),
            "categorical_distributions": pune_cat_dists,
            "numerical_statistics": pune_num_stats,
        },
    }

    output_json = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "dataset_profile.json")
    output_json = os.path.abspath(output_json)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit completed successfully! Saved JSON report to {output_json}")
    return audit_results


if __name__ == "__main__":
    main()
