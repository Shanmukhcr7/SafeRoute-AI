# Phase 3: Analytics & Intelligence Engine

## Architecture Overview
Rather than standard static EDA (Exploratory Data Analysis), Phase 3 implements an **Analytics & Intelligence Engine**. This pipeline natively queries the SQLite database to generate Key Performance Indicators (KPIs), comparative analytics, correlation strengths, and anomaly detection. 

All intelligence is serialized into `.json` payloads, making the future Streamlit Dashboard purely a presentation layer that loads instantly without running heavy queries on the fly.

## Components Implemented

1. **KPI Generator (`reports.py`)**: 
   Queries the entire database to extract the absolute truth metrics:
   - Total Accidents, Critical Zones count, Average Risk, Fatality Rate, Most Dangerous Hour.
   - Saves Top 10 rankings natively back into `road_risk.db` for instant dashboard loading.

2. **Trend & Correlation Engine (`trend_analysis.py`)**:
   Automatically identifies shifts. Calculates percentage increases:
   - Example: Night Driving -> `↑ X% severity increase`
   - Example: Rain -> `↑ X% fatality increase`
   - Calculates Pearson correlations and tags them as Strong/Moderate/Weak for textual reports.

3. **Machine Learning Anomaly Detection (`anomaly_detection.py`)**:
   Utilizes `IsolationForest` (unsupervised ML) to scan the H3 spatial statistics and flag specific regions that break the standard statistical model (e.g., highly abnormal weather-to-accident ratios).

4. **AI-Generated Insights (`insights.py`)**:
   Rule-based logic that reads the statistics of the worst zones and generates a paragraph-level textual summary explaining *why* it's dangerous, ending with a suggested real-world action (e.g., "Increase Warning Signage").

5. **Dashboard Export Orchestrator (`dashboard_export.py`)**:
   The master script that runs all the above classes and outputs highly optimized JSON files:
   - `kpi_summary.json`
   - `trend_analysis.json`
   - `correlations.json`
   - `anomalies.json`
   - `insights.json`

## Real-World Value
This sets up the **Traffic Intelligence Dashboard (Phase 9)**. When the dashboard loads, it simply points to these JSONs to render Animated KPIs, Insights, and Rankings in milliseconds.

## Next Steps Pivot
Per the latest architectural decision, instead of moving to ML immediately, we are jumping into **Phase 6: GIS Visualization Engine** early! This will allow us to visualize the `risk_zone.geojson` map with our new stats immediately to validate the pipeline visually.
