# Phase 8: Traffic Intelligence Command Center

## Architectural Shift
At the user's explicit request, Phase 8 was moved up in the pipeline to serve as the unified visualization layer for all previous engines (GIS, Context, Simulation, AI). The UI is built using Streamlit but is structured as a multi-page **Mission Control System** featuring a professional dark theme and glassmorphism CSS.

## The Modules

1. **Mission Control (`1_Mission_Control.py`)**:
   - The homepage of the application.
   - Features real-time KPI cards fetching directly from the SQLite database (Active Twins, Average Risk, Critical Alerts).
   - Contains the **Alert Center** which parses the SQLite `alerts` table and renders color-coded notifications based on severity.

2. **Live Map & Scenario Simulator (`2_Live_Map.py`)**:
   - Embeds the massive `interactive_risk_map.html` generated in Phase 4.
   - Introduces the **Scenario Simulator**: A sidebar where users can change Weather, Time, and Driver Profiles. These inputs are immediately pumped through the **Context Engine** and **AI Predictor Engine**, outputting live SHAP explanation breakdowns (e.g., *Rain: +15%, Night: +10%*) directly to the UI.

3. **AI Analytics (`3_AI_Analytics.py`)**:
   - Reads the `models/metadata.json` and `evaluation_report.json` generated in Phase 5.
   - Displays the Champion Model metadata, global Feature Importance charts, and the complete Classification Report.

4. **Digital Twin Mission Playback (`4_Vehicle_Simulation.py`)**:
   - A timeline scrubber (slider) that fetches from the `vehicle_telemetry` table.
   - As the user moves the slider, it replays the exact state (Speed, Zone, Risk, Status) of every simulated vehicle at that precise second.

5. **System Health (`5_System_Health.py`)**:
   - Enterprise monitoring page checking the liveliness of the SQLite DB, AI Models, Map files, and underlying OS hardware (CPU/RAM).
