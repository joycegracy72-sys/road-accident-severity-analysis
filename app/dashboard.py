"""Interactive Road Safety Explorer Dashboard (Streamlit & Folium).

Project Title: Road Accident Severity Analysis and Prediction Using Machine Learning
Scope: Great Britain Personal-Injury Collisions (2022 STATS19 Dataset)
"""

from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils import (
    CLEANED_GEO_DATA_PATH,
    PROCESSED_DATA_DIR,
    SAVED_MODEL_PATH,
    MODEL_METADATA_PATH,
    ALL_MODEL_FEATURES,
    TARGET_MAPPING,
)

# Page Configuration
st.set_page_config(
    page_title="Road Accident Severity Explorer (GB 2022)",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Clean, Google-Maps Inspired Explorer Look
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #5f6368;
        margin-bottom: 16px;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #dadce0;
        box-shadow: 0 1px 3px rgba(60,64,67,0.1);
        text-align: center;
    }
    .kpi-title {
        font-size: 13px;
        color: #5f6368;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #202124;
    }
    .kpi-sub {
        font-size: 12px;
        color: #70757a;
    }
    .disclaimer-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1a73e8;
        padding: 12px;
        border-radius: 4px;
        font-size: 13px;
        color: #3c4043;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_geo_data() -> pd.DataFrame:
    """Loads validated geographic dataset (105,982 records)."""
    return pd.read_parquet(CLEANED_GEO_DATA_PATH)


@st.cache_data
def load_hotspots_data() -> pd.DataFrame:
    """Loads DBSCAN hotspot clusters summary."""
    clusters_path = PROCESSED_DATA_DIR / "hotspots_clusters.csv"
    if clusters_path.exists():
        return pd.read_csv(clusters_path)
    return pd.DataFrame()


@st.cache_resource
def load_model_pipeline():
    """Loads trained ML model pipeline and metadata."""
    if not SAVED_MODEL_PATH.exists():
        return None, None
    pipeline = joblib.load(SAVED_MODEL_PATH)
    meta = {}
    if MODEL_METADATA_PATH.exists():
        with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
    return pipeline, meta


def main():
    # Header Section
    st.markdown('<div class="main-header">Road Accident Severity Analysis and Prediction Using Machine Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive Road-Safety Geographic Explorer & Severity Estimation | Scope: Great Britain (2022 STATS19 Reported Personal-Injury Collisions)</div>', unsafe_allow_html=True)

    # Load Data
    with st.spinner("Loading road safety datasets..."):
        df_geo = load_geo_data()
        df_hotspots = load_hotspots_data()
        pipeline, model_meta = load_model_pipeline()

    # Sidebar Filters
    st.sidebar.header("🔍 Collision Filters")
    st.sidebar.caption("Filter historical 2022 collision records across Great Britain.")

    # Severity Filter
    severity_options = ["All Severities", "Fatal (1)", "Serious (2)", "Slight (3)"]
    selected_severity = st.sidebar.selectbox("Collision Severity", severity_options, index=0)

    # Settlement Area Filter
    urban_options = ["All Areas", "Urban", "Rural"]
    selected_area = st.sidebar.selectbox("Settlement Classification", urban_options, index=0)

    # Month Filter
    month_names = {
        0: "All Months", 1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August", 9: "September",
        10: "October", 11: "November", 12: "December"
    }
    selected_month = st.sidebar.selectbox("Month of 2022", list(month_names.keys()), format_func=lambda x: month_names[x])

    # Speed Limit Filter
    speed_limits = ["All Speeds", 20, 30, 40, 50, 60, 70]
    selected_speed = st.sidebar.selectbox("Speed Limit (mph)", speed_limits, index=0)

    # Road Type Filter
    road_type_names = {
        0: "All Road Types",
        1: "Roundabout",
        2: "One-way street",
        3: "Dual carriageway",
        6: "Single carriageway",
        7: "Slip road",
    }
    selected_road_type = st.sidebar.selectbox("Road Layout", list(road_type_names.keys()), format_func=lambda x: road_type_names[x])

    # Apply Filters to Full Geo Dataset
    filtered_df = df_geo.copy()

    if selected_severity == "Fatal (1)":
        filtered_df = filtered_df[filtered_df["collision_severity"] == 1]
    elif selected_severity == "Serious (2)":
        filtered_df = filtered_df[filtered_df["collision_severity"] == 2]
    elif selected_severity == "Slight (3)":
        filtered_df = filtered_df[filtered_df["collision_severity"] == 3]

    if selected_area == "Urban":
        filtered_df = filtered_df[filtered_df["urban_or_rural_area"] == 1]
    elif selected_area == "Rural":
        filtered_df = filtered_df[filtered_df["urban_or_rural_area"] == 2]

    if selected_month != 0:
        filtered_df = filtered_df[filtered_df["collision_month"] == selected_month]

    if selected_speed != "All Speeds":
        filtered_df = filtered_df[filtered_df["speed_limit"] == int(selected_speed)]

    if selected_road_type != 0:
        filtered_df = filtered_df[filtered_df["road_type"] == selected_road_type]

    # Compute Exact KPI Counts on the Filtered Dataset
    total_matches = len(filtered_df)
    fatal_count = int((filtered_df["collision_severity"] == 1).sum())
    serious_count = int((filtered_df["collision_severity"] == 2).sum())
    slight_count = int((filtered_df["collision_severity"] == 3).sum())

    # Summary KPI Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Collisions</div>
            <div class="kpi-value">{total_matches:,}</div>
            <div class="kpi-sub">Matching Filters (100% of data)</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        fatal_pct = (fatal_count / total_matches * 100) if total_matches > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #d9534f;">
            <div class="kpi-title" style="color: #d9534f;">Fatal Collisions</div>
            <div class="kpi-value">{fatal_count:,}</div>
            <div class="kpi-sub">{fatal_pct:.2f}% of filtered total</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        serious_pct = (serious_count / total_matches * 100) if total_matches > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #f0ad4e;">
            <div class="kpi-title" style="color: #d97706;">Serious Collisions</div>
            <div class="kpi-value">{serious_count:,}</div>
            <div class="kpi-sub">{serious_pct:.2f}% of filtered total</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        slight_pct = (slight_count / total_matches * 100) if total_matches > 0 else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #5bc0de;">
            <div class="kpi-title" style="color: #0284c7;">Slight Collisions</div>
            <div class="kpi-value">{slight_count:,}</div>
            <div class="kpi-sub">{slight_pct:.2f}% of filtered total</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Tabs: Map Explorer, Hotspot Detail, Model Demonstration
    tab_map, tab_hotspots, tab_model = st.tabs(["🗺️ Geographic Map Explorer", "📍 Top Hotspot Clusters", "🤖 Machine Learning Severity Predictor"])

    with tab_map:
        st.subheader("Great Britain Collision & Hotspot Map")
        st.caption("Displays acute DBSCAN collision clusters (EPSG:27700 projected clustering) and sample collision points. Map center: Great Britain.")

        if total_matches == 0:
            st.warning("No collision records match the currently selected filter combination. Please broaden your filters in the sidebar.")
        else:
            # Center of Great Britain
            m = folium.Map(
                location=[54.5, -2.5],
                zoom_start=6,
                tiles="CartoDB positron",
            )

            # Overlay Top DBSCAN Hotspots
            if not df_hotspots.empty:
                hotspot_group = folium.FeatureGroup(name="DBSCAN Hotspot Clusters (Top 50)")
                for _, row in df_hotspots.head(50).iterrows():
                    radius = min(max(row["total_collisions"] / 25, 6), 25)
                    popup_html = f"""
                    <div style='font-family: sans-serif; font-size: 12px; width: 220px;'>
                        <b>Hotspot Cluster #{int(row['cluster_id'])}</b><br>
                        <b>Total Collisions (2022):</b> {int(row['total_collisions'])}<br>
                        <b>Fatal:</b> {int(row['fatal_count'])} ({row['fatal_rate_pct']}%)<br>
                        <b>Serious:</b> {int(row['serious_count'])} ({row['serious_rate_pct']}%)<br>
                        <b>Slight:</b> {int(row['slight_count'])}<br>
                        <b>Speed Limit:</b> {int(row['dominant_speed_limit'])} mph<br>
                        <b>Area:</b> {row['dominant_urban_rural']}
                    </div>
                    """
                    folium.CircleMarker(
                        location=[row["center_latitude"], row["center_longitude"]],
                        radius=radius,
                        color="#d9534f",
                        fill=True,
                        fill_color="#d9534f",
                        fill_opacity=0.6,
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"Cluster #{int(row['cluster_id'])}: {int(row['total_collisions'])} collisions",
                    ).add_to(hotspot_group)
                hotspot_group.add_to(m)

            # Sample individual collisions for browser responsiveness
            max_markers = 1000
            sample_size = min(total_matches, max_markers)
            sample_df = filtered_df.sample(n=sample_size, random_state=42) if total_matches > max_markers else filtered_df

            marker_cluster = MarkerCluster(name=f"Sample Collisions ({sample_size:,} displayed)").add_to(m)
            severity_colors = {1: "#d9534f", 2: "#f0ad4e", 3: "#5bc0de"}

            for _, row in sample_df.iterrows():
                sev = int(row["collision_severity"])
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=4,
                    color=severity_colors.get(sev, "#5bc0de"),
                    fill=True,
                    fill_opacity=0.8,
                    tooltip=f"Severity: {TARGET_MAPPING.get(sev, 'Unknown')} | Vehicles: {row['number_of_vehicles']} | Speed: {row['speed_limit']} mph",
                ).add_to(marker_cluster)

            folium.LayerControl().add_to(m)

            st_folium(m, width="100%", height=550)

            if total_matches > max_markers:
                st.info(f"ℹ️ Map rendering is capped at a random sample of {max_markers:,} markers to maintain responsive browser performance. The KPI metrics and summary statistics above represent all {total_matches:,} filtered collisions.")

    with tab_hotspots:
        st.subheader("High-Density Hotspot Analysis (EPSG:27700 British National Grid)")
        st.markdown("""
        **Methodological Note**: Hotspot clusters were computed using **DBSCAN** applied directly to native British National Grid Easting and Northing coordinates in true meters (`eps=250m`, `min_samples=15`).
        High collision volume reflects concentrated traffic exposure (e.g., complex multi-lane junctions) and must not be conflated with per-mile collision risk without traffic flow denominators.
        """)
        
        if not df_hotspots.empty:
            st.dataframe(
                df_hotspots[[
                    "cluster_id", "total_collisions", "fatal_count", "serious_count",
                    "slight_count", "fatal_rate_pct", "serious_rate_pct",
                    "dominant_speed_limit", "dominant_urban_rural",
                    "center_latitude", "center_longitude"
                ]].head(30),
                use_container_width=True,
            )
        else:
            st.write("Hotspot summary data unavailable.")

    with tab_model:
        st.subheader("Machine Learning Severity Prediction Demo")
        st.markdown("""
        This interactive tool uses the trained **Balanced Random Forest Pipeline** (selected for highest Macro-F1 across Fatal, Serious, and Slight categories) to predict conditional collision severity based on pre-crash environmental and roadway attributes.
        """)

        with st.form("prediction_form"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                form_vehicles = st.number_input("Number of Vehicles Involved", min_value=1, max_value=10, value=2)
                form_speed = st.selectbox("Posted Speed Limit (mph)", [20, 30, 40, 50, 60, 70], index=1)
                form_road_type = st.selectbox("Road Layout", [
                    (6, "Single carriageway"),
                    (3, "Dual carriageway"),
                    (1, "Roundabout"),
                    (2, "One-way street"),
                    (7, "Slip road"),
                ], format_func=lambda x: x[1])
                form_road_class = st.selectbox("First Road Class", [
                    (3, "A-Road"),
                    (1, "Motorway"),
                    (2, "A(M)"),
                    (4, "B-Road"),
                    (5, "C-Road"),
                    (6, "Unclassified"),
                ], format_func=lambda x: x[1])
            with col_b:
                form_weather = st.selectbox("Weather Conditions", [
                    (1, "Fine no high winds"),
                    (2, "Raining no high winds"),
                    (3, "Snowing no high winds"),
                    (4, "Fine + high winds"),
                    (5, "Raining + high winds"),
                    (7, "Fog or mist"),
                ], format_func=lambda x: x[1])
                form_surface = st.selectbox("Road Surface", [
                    (1, "Dry"),
                    (2, "Wet or damp"),
                    (3, "Snow"),
                    (4, "Frost or ice"),
                    (5, "Flood (>3cm deep)"),
                ], format_func=lambda x: x[1])
                form_light = st.selectbox("Lighting Conditions", [
                    (1, "Daylight"),
                    (4, "Darkness - lights lit"),
                    (5, "Darkness - lights unlit"),
                    (6, "Darkness - no lighting"),
                ], format_func=lambda x: x[1])
                form_urban = st.selectbox("Settlement Classification", [
                    (1, "Urban"),
                    (2, "Rural"),
                ], format_func=lambda x: x[1])
            with col_c:
                form_hour = st.slider("Hour of Day (0-23)", 0, 23, 17)
                form_month = st.slider("Month of Year (1-12)", 1, 12, 10)
                form_day = st.selectbox("Day of Week", [
                    (1, "Sunday"), (2, "Monday"), (3, "Tuesday"),
                    (4, "Wednesday"), (5, "Thursday"), (6, "Friday"), (7, "Saturday")
                ], index=5, format_func=lambda x: x[1])
                form_junction = st.selectbox("Junction Layout", [
                    (0, "Not at junction"),
                    (3, "T or staggered junction"),
                    (6, "Crossroads"),
                    (1, "Roundabout"),
                    (2, "Mini-roundabout"),
                    (8, "Private drive"),
                ], format_func=lambda x: x[1])

            submit_btn = st.form_submit_button("Predict Collision Severity", use_container_width=True)

        if submit_btn:
            if pipeline is None:
                st.error("Model pipeline artifact not found at models/trained_pipeline.joblib. Please ensure model training has been completed.")
            else:
                # Prepare single-row DataFrame with all 21 model features
                is_night_val = 1 if form_hour in [21, 22, 23, 0, 1, 2, 3, 4, 5] else 0
                input_data = {
                    "number_of_vehicles": [form_vehicles],
                    "speed_limit": [form_speed],
                    "collision_hour": [form_hour],
                    "collision_month": [form_month],
                    "first_road_class": [form_road_class[0]],
                    "road_type": [form_road_type[0]],
                    "junction_detail_historic": [form_junction[0]],
                    "junction_control": [4 if form_junction[0] != 0 else -1],
                    "second_road_class": [6 if form_junction[0] != 0 else 0],
                    "pedestrian_crossing_human_control_historic": [0],
                    "pedestrian_crossing_physical_facilities_historic": [0],
                    "light_conditions": [form_light[0]],
                    "weather_conditions": [form_weather[0]],
                    "road_surface_conditions": [form_surface[0]],
                    "special_conditions_at_site": [0],
                    "carriageway_hazards_historic": [0],
                    "urban_or_rural_area": [form_urban[0]],
                    "trunk_road_flag": [2],
                    "police_force": [1],  # Default force
                    "day_of_week": [form_day[0]],
                    "is_night": [is_night_val],
                }
                input_df = pd.DataFrame(input_data)
                
                prediction = pipeline.predict(input_df)[0]
                pred_label = TARGET_MAPPING.get(prediction, "Unknown")
                
                # Check for predict_proba
                has_proba = hasattr(pipeline, "predict_proba")
                if has_proba:
                    probas = pipeline.predict_proba(input_df)[0]
                    # Map classes
                    classes = pipeline.classes_
                    proba_dict = {TARGET_MAPPING.get(c, str(c)): probas[i] for i, c in enumerate(classes)}

                st.markdown("### Prediction Results")
                res_col1, res_col2 = st.columns([1, 2])
                with res_col1:
                    badge_color = "#d9534f" if prediction == 1 else ("#f0ad4e" if prediction == 2 else "#5bc0de")
                    st.markdown(f"""
                    <div style='background-color: {badge_color}; color: white; padding: 18px; border-radius: 8px; text-align: center;'>
                        <div style='font-size: 13px; text-transform: uppercase;'>Predicted Severity</div>
                        <div style='font-size: 26px; font-weight: bold;'>{pred_label}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with res_col2:
                    if has_proba:
                        st.markdown("**Estimated Class Probabilities:**")
                        for cls_name in ["Fatal", "Serious", "Slight"]:
                            prob = proba_dict.get(cls_name, 0.0)
                            st.write(f"**{cls_name}**: {prob*100:.1f}%")
                            st.progress(float(prob))

        # Ethical & Operational Disclaimer
        st.markdown("""
        <div class="disclaimer-box">
            <b>Educational & Research Disclaimer:</b> This machine learning model predicts the conditional severity of a collision given that an incident has already occurred. It does <b>not</b> predict whether a collision will occur. Model predictions are statistical estimates based on police-reported STATS19 data for Great Britain in 2022 and must not be used as an operational emergency dispatch decision system or for individual driver profiling.
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
