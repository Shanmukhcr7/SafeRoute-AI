# Phase 2: Risk Intelligence Engine

## Architecture Overview
This phase elevates traditional feature engineering into a **Hybrid Risk Intelligence Engine**. Rather than relying purely on static values or a purely black-box AI model, we engineered an explainable, hybrid engine. 

The engine groups all accidents by their Uber H3 Spatial Hexagon (`h3_index`) and calculates granular statistics. These statistics are fused into a dynamic `Risk Score` incorporating both historical density, environmental triggers, road geometry, and (in Phase 6) real-time XGBoost AI predictions.

## Feature Dictionary

| Feature | Description | Formula | Reason |
|---------|-------------|---------|--------|
| `accident_count` | Total historical accidents in the H3 Hexagon | `count(Num_Acc)` per `h3_index` | Base density of incidents. |
| `fatal_count` | Total fatal/severe injuries | `sum(fatalities)` | Identifies lethal zones vs minor fender-bender zones. |
| `rain_percentage` | Probability of rain during accident | `mean(is_rain) * 100` | Identifies aquaplaning and low-visibility hotspots. |
| `night_percentage` | Percentage of accidents occurring at night | `mean(is_night) * 100` | Flags unlit or dangerous nocturnal stretches. |
| `curve_percentage` | Percentage of accidents on curves | `mean(is_curve) * 100` | Flags sharp turns leading to loss of control. |
| `risk_score` | Normalized hybrid danger rating (0-100) | `0.4*Density + 0.2*Fatal + 0.15*Env + 0.1*Geo + 0.05*Time + 0.1*AI` | Provides a scientifically weighted actionable metric. |

## Outputs Generated
1. **`data/processed/processed_features.csv`**: Granular accident-level enhanced data.
2. **`data/processed/zone_statistics.csv`**: Hexagon-level aggregate statistics.
3. **`data/processed/risk_scores.csv`**: Hybrid scores, categorical labels (Safe, Low, Moderate, High, Critical), and explainability strings.
4. **`data/processed/risk_zone.geojson`**: Read-to-deploy GeoJSON file containing hexagonal Polygons and their embedded Risk Properties for Leaflet/Streamlit.
5. **`SQLite Tables`**: Integrated natively into `road_risk.db` under the `zone_statistics` and `risk_scores` tables.

## Explainability Module
The engine generates a human-readable `explanation` string for every zone. Example output stored in DB:
> " • Heavy Rain (54%)\n • Sharp Curves\n • High Fatality History"

This directly supports the interactive GIS mapping UI in Phase 5.
