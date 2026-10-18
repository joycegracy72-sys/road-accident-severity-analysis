"""Exploratory Data Analysis (EDA) for STATS19 2022 collision dataset."""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from src.utils import (
    CLEANED_MODEL_DATA_PATH,
    CLEANED_GEO_DATA_PATH,
    FIGURES_DIR,
    REPORTS_DIR,
    TARGET_MAPPING,
    TARGET_COL,
    setup_logger,
)

logger = setup_logger("eda_analysis")

# Set consistent matplotlib/seaborn style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})


def run_eda() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Loading cleaned model data from {CLEANED_MODEL_DATA_PATH}...")
    df = pd.read_parquet(CLEANED_MODEL_DATA_PATH)
    
    eda_stats = {}

    # 1. Target Distribution & Class Imbalance
    severity_counts = df[TARGET_COL].value_counts().sort_index()
    severity_labels = [TARGET_MAPPING[idx] for idx in severity_counts.index]
    severity_pcts = (severity_counts / len(df) * 100).round(2)
    
    eda_stats["target_counts"] = {TARGET_MAPPING[k]: int(v) for k, v in severity_counts.items()}
    eda_stats["target_percentages"] = {TARGET_MAPPING[k]: float(v) for k, v in severity_pcts.items()}
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(severity_labels, severity_counts.values, color=["#d9534f", "#f0ad4e", "#5bc0de"], edgecolor="black")
    ax.set_title("Distribution of Collision Severity (Great Britain, 2022)")
    ax.set_xlabel("Severity Classification")
    ax.set_ylabel("Number of Collisions")
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:,}\n({height/len(df)*100:.1f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(severity_counts.values) * 1.15)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "target_distribution.png")
    plt.close()
    logger.info("Saved target_distribution.png")

    # 2. Collisions by Month and Weekday
    month_counts = df["collision_month"].value_counts().sort_index()
    eda_stats["monthly_counts"] = {int(k): int(v) for k, v in month_counts.items()}
    
    weekday_counts = df["day_of_week"].value_counts().sort_index()
    weekday_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    eda_stats["weekday_counts"] = {weekday_labels[k-1]: int(v) for k, v in weekday_counts.items()}
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.plot(month_counts.index, month_counts.values, marker="o", color="#2c3e50", linewidth=2)
    ax1.set_title("Collisions by Month (2022)")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Collisions")
    ax1.set_xticks(range(1, 13))
    
    ax2.bar(weekday_labels, weekday_counts.values, color="#34495e", edgecolor="black")
    ax2.set_title("Collisions by Day of Week (2022)")
    ax2.set_xlabel("Day of Week")
    ax2.set_ylabel("Total Collisions")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "temporal_monthly_weekday.png")
    plt.close()
    logger.info("Saved temporal_monthly_weekday.png")

    # 3. Diurnal Cycle (Hour of Day) by Severity
    hour_severity = pd.crosstab(df["collision_hour"], df[TARGET_COL], normalize="columns") * 100
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hour_severity.index, hour_severity[1], marker="s", color="#d9534f", label="Fatal (% within Fatal)", linewidth=2)
    ax.plot(hour_severity.index, hour_severity[2], marker="^", color="#f0ad4e", label="Serious (% within Serious)", linewidth=1.8)
    ax.plot(hour_severity.index, hour_severity[3], marker="o", color="#5bc0de", label="Slight (% within Slight)", linewidth=1.5)
    ax.set_title("Normalized Hourly Profile by Collision Severity")
    ax.set_xlabel("Hour of Day (0-23)")
    ax.set_ylabel("Percentage within Severity Class (%)")
    ax.set_xticks(range(0, 24))
    ax.legend()
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "hourly_severity_profile.png")
    plt.close()
    logger.info("Saved hourly_severity_profile.png")

    # 4. Speed Limit vs Severity Distribution
    speed_ct = pd.crosstab(df["speed_limit"], df[TARGET_COL], margins=True)
    speed_pct_fatal = (pd.crosstab(df["speed_limit"], df[TARGET_COL], normalize="index") * 100)
    eda_stats["speed_limit_fatal_rate"] = {int(k): float(v) for k, v in speed_pct_fatal[1].round(2).items()}
    eda_stats["speed_limit_serious_rate"] = {int(k): float(v) for k, v in speed_pct_fatal[2].round(2).items()}
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    # Collision volume by speed limit
    ax1.bar([str(s) for s in speed_ct.index[:-1]], speed_ct["All"][:-1], color="#2980b9", edgecolor="black")
    ax1.set_title("Reported Collisions by Posted Speed Limit")
    ax1.set_xlabel("Posted Speed Limit (mph)")
    ax1.set_ylabel("Collision Volume")
    
    # Severity proportions across speed limits
    speed_pct_fatal[[1, 2, 3]].plot(kind="bar", stacked=True, ax=ax2,
                                     color=["#d9534f", "#f0ad4e", "#5bc0de"], edgecolor="black")
    ax2.set_title("Severity Proportion by Posted Speed Limit")
    ax2.set_xlabel("Posted Speed Limit (mph)")
    ax2.set_ylabel("Proportion within Speed Limit (%)")
    ax2.legend(["Fatal", "Serious", "Slight"], loc="upper left")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "speed_limit_severity.png")
    plt.close()
    logger.info("Saved speed_limit_severity.png")

    # 5. Road Surface and Weather Conditions
    surface_labels = {1: "Dry", 2: "Wet/Damp", 3: "Snow", 4: "Frost/Ice", 5: "Flood", 9: "Unknown", -1: "Missing"}
    weather_labels = {1: "Fine (no wind)", 2: "Rain (no wind)", 3: "Snow (no wind)", 4: "Fine + wind",
                      5: "Rain + wind", 6: "Snow + wind", 7: "Fog/mist", 8: "Other", 9: "Unknown", -1: "Missing"}
    
    df["surface_name"] = df["road_surface_conditions"].map(surface_labels).fillna("Other")
    df["weather_name"] = df["weather_conditions"].map(weather_labels).fillna("Other")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_surfaces = df["surface_name"].value_counts().head(5)
    ax.barh(top_surfaces.index[::-1], top_surfaces.values[::-1], color="#16a085", edgecolor="black")
    ax.set_title("Top Road Surface Conditions in Reported Collisions (2022)")
    ax.set_xlabel("Total Collisions")
    for i, v in enumerate(top_surfaces.values[::-1]):
        ax.text(v + 500, i, f"{v:,} ({v/len(df)*100:.1f}%)", va="center", fontsize=10)
    ax.set_xlim(0, max(top_surfaces.values) * 1.18)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "road_surface_conditions.png")
    plt.close()
    logger.info("Saved road_surface_conditions.png")

    # 6. Urban vs Rural Severity Proportions
    urban_rural_map = {1: "Urban", 2: "Rural", 3: "Unallocated"}
    df["urban_rural_name"] = df["urban_or_rural_area"].map(urban_rural_map).fillna("Unknown")
    ur_crosstab = pd.crosstab(df["urban_rural_name"], df[TARGET_COL], normalize="index") * 100
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ur_crosstab[[1, 2, 3]].plot(kind="bar", stacked=True, ax=ax,
                                 color=["#d9534f", "#f0ad4e", "#5bc0de"], edgecolor="black")
    ax.set_title("Severity Distribution: Urban vs Rural (2022)")
    ax.set_xlabel("Settlement Area")
    ax.set_ylabel("Proportion within Area (%)")
    ax.legend(["Fatal", "Serious", "Slight"], loc="lower right")
    plt.xticks(rotation=0)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "urban_rural_severity.png")
    plt.close()
    logger.info("Saved urban_rural_severity.png")
    
    eda_stats["urban_rural_rates"] = {
        area: {
            "Fatal_pct": float(round(ur_crosstab.loc[area, 1], 2)),
            "Serious_pct": float(round(ur_crosstab.loc[area, 2], 2)),
            "Slight_pct": float(round(ur_crosstab.loc[area, 3], 2)),
            "Total_count": int((df["urban_rural_name"] == area).sum())
        }
        for area in ur_crosstab.index if area in ["Urban", "Rural"]
    }

    # Save detailed numerical summary for documentation
    summary_path = REPORTS_DIR / "eda_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(eda_stats, f, indent=2)
    logger.info(f"EDA numerical statistics saved to {summary_path}")


if __name__ == "__main__":
    run_eda()
