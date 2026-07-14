# 🚦 SafeRoute-AI: Dynamic Road Accident Risk Zone Detection

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-green.svg)
![Build](https://img.shields.io/badge/build-passing-success)

A next-generation **Advanced Driver Assistance System (ADAS) Simulator** and **Route Analysis Engine**. SafeRoute-AI shifts traditional road-risk analysis from static heatmaps to a live, machine-learning-powered **Digital Twin Simulator**. 

By combining 15 years of authentic French accident datasets (220,000+ GPS records) with Uber's H3 spatial indexing and a dynamically adapting HistGradientBoosting Classifier, this project models exactly how safe a route is *right now*, under current environmental conditions.

---

## 🌟 Key Features

1. **Authentic Spatial Data Indexing**
   - **Uber H3 Hexagons**: We compress and aggregate 220,000+ historical accident coordinates into rigid, mathematically uniform hexagonal grids (Resolution 8).
   - **Rigorous Thresholds**: To prevent map clutter, the system filters out statistical noise. It strictly isolates the top 5% of deadly intersections in France (>40 historical accidents) to ensure warnings are actually meaningful.

2. **Machine Learning AI Predictor**
   - **HistGradientBoosting Classifier**: Trained on massive CSV datasets (`caracteristics.csv`, `users.csv`), the ML engine learned the correlations between environmental factors (Lighting, Weather) and accident severity (Fatal, Hospitalized, Minor).
   - **Dynamic Risk Multipliers**: At night, or during rain, the ML model dynamically calculates real-time probabilities. A historically "Moderate" risk intersection can dynamically jump to "CRITICAL" if the weather degrades.

3. **Live ADAS Route Simulation**
   - **Environment Simulator**: A beautiful Streamlit Command Center allows users to set Weather and Time-Of-Day conditions. 
   - **Smooth JS Animation**: The vehicle traces accurate GPS route strings via Leaflet and Turf.js, perfectly aligning its top-down SVG chassis with the current mathematical bearing.
   - **500m Lookahead Radar**: The digital twin scans 500 meters ahead on the route geometry and triggers pop-up alerts before the car actually enters a dangerous hexagon.

4. **Automated AI Analytics**
   - **Global Feature Importance**: Evaluates what factors drive the ML's decisions.
   - **ROC-AUC & Classification Reports**: Achieved a 0.79 cross-validation Risk F1 Score and an 0.80 AUC curve.

---

## 🛠️ Tech Stack

*   **Backend / Processing**: Python 3.10, Pandas, SQLite3
*   **Machine Learning**: Scikit-Learn (`HistGradientBoostingClassifier`, `permutation_importance`)
*   **Spatial Math**: `h3-py` (v4), `turf.js`
*   **Frontend Dashboard**: Streamlit, Leaflet.js (`folium`)
*   **UI/UX**: Custom `config.toml` enforcing a pristine Light Theme aesthetic with native glassmorphism styling.

---

## 🚀 How to Run the Project

Running the project is incredibly simple. You do not need to boot up separate terminals.

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch the Dashboard**:
   - On Windows, simply double-click the **`start_project.bat`** file in the root directory.
   - *Alternatively, run*: `streamlit run dashboard/app.py`

3. **Navigating the UI**:
   - **🌍 France Risk Map**: View a macro-level rendering of all Critical and Fatal intersections mapped across the entire country.
   - **🚗 Live Map (ADAS Simulator)**: Select an environment (Clear, Rain) and Time (Day, Night), then click "Start Navigation" to watch the ML model predict risks live as the car drives from Paris to Lyon.
   - **🧠 AI Analytics**: Review the actual Machine Learning metrics, Confusion Matrices, and Feature Importances extracted automatically during the model training phase.

---

## 📊 Evaluation Metrics

Our ML-augmented H3 Spatial method drastically outperforms traditional heuristic bounding boxes or K-Means clustering in a dynamic environment:

| Method | Silhouette ↑ | Risk F1 ↑ | Alert Latency |
| :--- | :--- | :--- | :--- |
| **Heuristic Black-Spot** | N/A | 0.58 | 10 ms |
| **K-Means Clustering** | 0.45 | 0.64 | 48 ms |
| **Uber H3 Spatial Grids (Base)** | 0.65 | 0.70 | **5 ms** |
| **Proposed H3 + HistGradientBoosting** | **0.65** | **0.79** | 12 ms |

---

## 🏗️ Project Architecture

```text
road-risk-ai/
├── adas/
│   ├── ml_predictor.py     # Loads the .pkl model & calculates dynamic multipliers
│   └── route_analyzer.py   # Scans GPS routes against the SQLite H3 Database
├── dashboard/
│   ├── app.py              # Main Streamlit Entry Point
│   ├── components/
│   │   └── smooth_simulator.html  # JS/Leaflet Animation Engine
│   └── pages/
│       ├── 1_France_Risk_Map.py   # Global View
│       ├── 2_Live_Map.py          # The Simulator
│       └── 3_AI_Analytics.py      # Automated Model Reports
├── database/
│   └── road_risk.db        # Pre-calculated 89,000+ authentic French accident zones
├── models/
│   ├── dynamic_risk_model.pkl       # Trained ML Artifact
│   └── evaluation/
│       └── evaluation_report.json   # Auto-generated ROC/F1 matrices
└── scripts/
    ├── init_real_zones.py  # Generates database from raw CSVs
    └── train_ml_model.py   # Trains HistGradientBoosting and outputs evaluations
```
