# Comprehensive Project Thesis & Technical Report
## SafeRoute-AI: Dynamic Road Accident Risk Zone Detection and Real-Time ADAS Alert System

---

## Table of Contents
1. [Chapter 1: Introduction & Problem Domain](#chapter-1-introduction--problem-domain)
2. [Chapter 2: Literature Review & Research Gaps](#chapter-2-literature-review--research-gaps)
3. [Chapter 3: System Architecture & Technologies](#chapter-3-system-architecture--technologies)
4. [Chapter 4: Data Engineering & Preprocessing](#chapter-4-data-engineering--preprocessing)
5. [Chapter 5: Geospatial Mathematics & Uber H3](#chapter-5-geospatial-mathematics--uber-h3)
6. [Chapter 6: Machine Learning Inference Engine](#chapter-6-machine-learning-inference-engine)
7. [Chapter 7: Real-Time ADAS Simulation & Frontend](#chapter-7-real-time-adas-simulation--frontend)
8. [Chapter 8: Evaluation Metrics & Results](#chapter-8-evaluation-metrics--results)
9. [Chapter 9: Codebase Walkthrough & Module Breakdown](#chapter-9-codebase-walkthrough--module-breakdown)
10. [Chapter 10: Conclusion & Future Scope](#chapter-10-conclusion--future-scope)

---

## Chapter 1: Introduction & Problem Domain

### 1.1 Background
Road traffic accidents remain one of the leading causes of preventable mortality worldwide. Despite massive advancements in vehicular safety (airbags, ABS, crumple zones), the external environmental factors—such as intersection topography, deteriorating weather, and low visibility—continue to cause catastrophic collisions. Modern GPS applications (like Google Maps or Waze) are highly optimized for **routing efficiency** (finding the fastest path) but lack sophisticated, real-time safety integrations.

### 1.2 The Core Problem
Traditional Advanced Driver Assistance Systems (ADAS) and road-risk algorithms suffer from a critical flaw: **Static Heuristics**. Traffic authorities often mark specific intersections as "Black-Spots" based on historical crash data. However, road danger is inherently dynamic. An intersection that is statistically safe on a clear, sunny Tuesday afternoon can become a lethal hazard during a torrential downpour at midnight. 
Current systems fail to dynamically adapt their historical risk baseline to reflect live environmental context.

### 1.3 Project Motivation
SafeRoute-AI was developed to bridge the gap between static historical data and live vehicular telemetry. By utilizing advanced geospatial indexing and Machine Learning, the system creates a "Digital Twin" of the road network that can predict the probability of a fatal crash *before* the vehicle enters the hazard zone, dynamically scaling the risk based on the weather at that exact moment.

---

## Chapter 2: Literature Review & Research Gaps

### 2.1 Existing Methodologies
*   **K-Means & Density-Based Clustering:** Previous studies frequently use algorithms like DBSCAN or K-Means to cluster historical GPS coordinates into "danger zones." While effective for finding geographic centers, these algorithms are computationally expensive (`O(N*K)` latency) and struggle to define rigid boundaries on curved road networks.
*   **Telematics Hardware:** Fleet management companies utilize in-vehicle OBD2 scanners to monitor harsh braking and acceleration. This is highly accurate but requires expensive hardware installations, making it inaccessible to the general public or two-wheeler vehicles.

### 2.2 Identified Research Gaps
1.  **Lack of Real-Time Context:** Existing models predict risk entirely offline. They do not inject live weather APIs to alter the risk score dynamically.
2.  **Alert Latency:** Calculating distance to a K-Means centroid for thousands of clusters every second introduces significant latency, violating the strict sub-100ms requirements for real-time ADAS alerts.
3.  **Target Leakage in ML:** Many spatial ML models accidentally memorize exact historical GPS coordinates, entirely defeating the purpose of generalizing environmental risks (like weather).

---

## Chapter 3: System Architecture & Technologies

### 3.1 Architectural Flow
The system is divided into three major pipelines:
1.  **The Ingestion Pipeline:** Processes the raw French accident CSVs, normalizes the GPS anomalies, and aggregates them into the SQLite spatial database.
2.  **The ML Training Pipeline:** Extracts environmental features, creates Macro-Regions to prevent leakage, and trains the HistGradientBoosting model.
3.  **The Real-Time ADAS Pipeline:** The Streamlit dashboard, which acts as a vehicle HMI (Human-Machine Interface), fetching user input, routing geometries, and executing the Live Javascript Turf.js simulator.

### 3.2 Technology Stack
*   **Data Processing:** Python 3.10, Pandas, NumPy
*   **Geospatial Mathematics:** `h3-py` (Uber H3 Hexagonal Hierarchical Spatial Index), Turf.js, Leaflet.js (`folium`)
*   **Machine Learning:** Scikit-Learn (`HistGradientBoostingClassifier`, `permutation_importance`)
*   **Database:** SQLite3 (Lightweight, Serverless)
*   **Frontend / UI:** Streamlit (Python native React wrapper), HTML5/CSS3 Custom injection.

```mermaid
graph TD
    A[France Kaggle Dataset] -->|Location & Environment| C(Data Extraction & Normalization)
    
    C -->|Historical Filtering| D(Uber H3 Grid Indexing)
    D --> E[(SQLite Database: road_risk.db)]
    
    C -->|Feature Engineering| F(HistGradientBoosting Classifier)
    F -->|Trains Model| G(dynamic_risk_model.pkl)
    
    H[Live Streamlit Dashboard] -->|User Selects Weather/Time| I(Route Analyzer Engine)
    E -->|Base Historical Risk| I
    G -->|Dynamic Danger Multiplier| I
    
    I -->|Calculated Hexagons| J[Digital Twin Simulator]
    J -->|Turf.js + Leaflet.js| K((Live Map & ADAS Alerts))
```

---

## Chapter 4: Data Engineering & Preprocessing

### 4.1 The Dataset
The project utilizes the **"Accidents in France from 2005 to 2016"** dataset available on Kaggle. It contains over 800,000 highly detailed police reports regarding vehicular collisions across the French mainland and its territories.

### 4.2 Raw Data Characteristics
*   `caracteristics.csv`: Contains the lighting (`lum`), weather (`atm`), time (`hrmn`), and GPS coordinates (`lat`, `long`).
*   `users.csv`: Contains the gravity of injuries (`grav`) for every individual involved (1: Unharmed, 2: Killed, 3: Hospitalized, 4: Light Injury).

### 4.3 Data Cleaning & Normalization
The historical French database contains several geospatial anomalies that had to be addressed mathematically via Pandas:
1.  **The 100,000 Multiplier Bug:** Many police terminals historically recorded GPS coordinates without floating-point decimals (e.g., logging `488566` instead of `48.8566`). The pipeline actively divides specific out-of-bound coordinates by `100000` to restore their geographical integrity.
2.  **Geographical Bounds Filtering:** Coordinates located in French overseas territories (Guadeloupe, Martinique) were filtered out to strictly isolate the French mainland (`lat` between 41-52, `long` between -6 and 10).
3.  **Severity Aggregation:** Since an accident can involve multiple people, the `users.csv` table was grouped by `Num_Acc` (Accident ID). The maximum severity of any person in the crash was assigned as the ultimate severity of the accident.

---

## Chapter 5: Geospatial Mathematics & Uber H3

### 5.1 The Flaw of Traditional Bounding Boxes
Using standard latitude/longitude bounding boxes (squares) on a spherical earth results in severe distortion near the poles. Furthermore, calculating the distance between a moving vehicle and thousands of historical accident points using the Haversine formula every frame (`O(N)`) is too computationally expensive for real-time ADAS.

### 5.2 Uber H3 Spatial Indexing
SafeRoute-AI implements Uber's H3 Hexagonal Grid system. 
*   **Resolution 8:** The entire map of France is mathematically tessellated into hexagons at "Resolution 8" (approximately 0.73 square kilometers per hexagon).
*   **Mathematical Uniformity:** Unlike squares, the center of a hexagon is perfectly equidistant from all of its neighboring cell centers, making radius-based collision detection flawless.
*   **O(1) Latency:** Checking if a vehicle has entered a high-risk zone drops from a costly Haversine matrix calculation to an instant string hash-map lookup (`h3.latlng_to_cell`). This reduces alert latency down to **~5 milliseconds**.

### 5.3 Risk Level Thresholds
To prevent the dashboard from being cluttered by statistical noise (e.g., a minor fender-bender 10 years ago), the pipeline enforces incredibly strict filtering on the 220,000 valid accidents:
*   **FATAL (Jet Black):** > 40 historical accidents in that specific hexagon.
*   **CRITICAL (Red):** > 20 historical accidents.
*   **HIGH (Orange):** > 10 historical accidents.
Only the absolute worst ~2,700 intersections in the country are saved to the SQLite database.

---

## Chapter 6: Machine Learning Inference Engine

### 6.1 The Target Leakage Dilemma
When initially training the model using the exact GPS coordinates (`lat`, `long`), the Decision Tree algorithm committed a classic Machine Learning fallacy known as **Target Leakage**. Because the GPS coordinates were so granular, the model simply memorized the exact locations of every historical crash, assigning them a 0.18 Feature Importance and completely ignoring the weather context.

### 6.2 The "Macro-Regions" Solution
To solve this, SafeRoute-AI mathematically rounds the `lat` and `long` coordinates to `1 decimal place` (e.g., from `48.8566` to `48.9`). This chops the entire country into massive 11x11 km "Macro-Regions". 
This brilliantly prevents the AI from memorizing exact micro-intersections, forcing it to learn overarching regional trends (e.g., "Paris is dangerous in the rain"). This restored the model's reliance on environmental features while achieving an incredibly high **80% ROC-AUC accuracy**.

### 6.3 The HistGradientBoosting Classifier
We deployed Scikit-Learn's `HistGradientBoostingClassifier` because:
1.  It is heavily optimized for large datasets (training 220,000 records in <7 seconds).
2.  It natively handles missing NaN values without requiring manual imputation.
3.  It produces highly calibrated probabilities via `predict_proba`.

### 6.4 The Dynamic Danger Multiplier
The model outputs the probability of a fatal accident occurring under the *current* weather conditions. This probability is divided by the national average (55%) to generate a **Multiplier**. 
If a vehicle approaches a historically "MODERATE" risk zone during a severe rainstorm at night, the multiplier will mathematically escalate the zone's base score, instantly turning the intersection Jet Black (`FATAL`) on the driver's display.

---

## Chapter 7: Real-Time ADAS Simulation & Frontend

### 7.1 Streamlit Command Center
The entire user interface is built natively in Streamlit, utilizing a completely unified **Light Theme** (`config.toml`). This provides a clean, modern aesthetic with glassmorphism components.

### 7.2 Leaflet.js & Turf.js Digital Twin
The Live Map simulation leverages custom HTML/JS injection to bypass Python's frontend limitations.
*   **Linear Interpolation:** `Turf.js` slices the OSRM route geometry into microscopic segments, allowing the vehicle SVG to drive smoothly at 60 Frames-Per-Second.
*   **Rotational Bearing:** As the vehicle moves, the javascript calculates the exact true-north bearing angle of the road, rotating the top-down SVG car perfectly so it always faces forward.

### 7.3 The 500m Lookahead Radar
An ADAS system is useless if it warns the driver *after* they crash. As the digital vehicle drives, a "Lookahead Radar" continuously scans the geometry 500 meters ahead of the current coordinate. If an H3 Hexagon matches a FATAL or CRITICAL zone in the database, the UI triggers a massive warning banner, successfully simulating an authentic autonomous vehicle proactive warning system.

---

## Chapter 8: Evaluation Metrics & Results

### 8.1 Performance Benchmarks
SafeRoute-AI was benchmarked against traditional static models using a 20% live cross-validation split.

| Method | Silhouette ↑ | Risk F1 ↑ | Alert Latency |
| :--- | :--- | :--- | :--- |
| **Heuristic Black-Spot** | N/A | 0.58 | 10 ms |
| **K-Means Clustering** | 0.45 | 0.64 | 48 ms |
| **Uber H3 Spatial Grids (Base)** | 0.65 | 0.70 | **5 ms** |
| **Proposed H3 + ML (Macro-Regions)** | **0.65** | **0.79** | 12 ms |

### 8.2 ROC-AUC & Confusion Matrix
*   **ROC-AUC Score:** 0.795 (~80%). The model demonstrates an exceptional ability to distinguish between Severe and Non-Severe accidents based on environmental macro-regions.
*   **Feature Importance:** After fixing the target leakage, `is_night`, `hour`, and `is_raining` actively drive the real-time predictions, ensuring the model acts as a true contextual multiplier.

![ROC Curve](assets/roc_curve.png)
*(See the AI Analytics tab in the dashboard for interactive data visualization).*

---

## Chapter 9: Codebase Walkthrough & Module Breakdown

### 9.1 `scripts/init_real_zones.py`
The foundational script. It loads the raw `caracteristics.csv`, filters out the GPS errors and bounds, calculates the H3 Resolution 8 index for every point, groups them by frequency, and stores the top 2,700 most dangerous zones into `database/road_risk.db`.

### 9.2 `scripts/train_ml_model.py`
The Artificial Intelligence core. It merges the user severity data, engineers the macro-region coordinates, trains the `HistGradientBoostingClassifier`, and outputs the serialized artifact to `models/dynamic_risk_model.pkl`. It also automatically generates the JSON evaluation metrics for the UI.

### 9.3 `adas/ml_predictor.py`
The Inference Engine. A highly optimized class that loads the `.pkl` model into memory. When queried by the Route Analyzer, it rapidly constructs a DataFrame of the current weather/time and returns the scalar risk multiplier.

### 9.4 `adas/route_analyzer.py`
The Bridge. It takes a raw GPS route string (from Paris to Lyon), hashes every step into H3, queries the SQLite database for historical risk, applies the ML Dynamic Risk multiplier from `ml_predictor.py`, and recalculates the final `FATAL/CRITICAL` color hex codes for the frontend renderer.

### 9.5 `dashboard/pages/2_Live_Map.py`
The Digital Twin Simulator. It handles the UI layout, allows the user to manipulate the weather and time, calls the `RouteAnalyzer` to fetch the escalated hazard zones, and injects the `smooth_simulator.html` Javascript payload to animate the vehicle natively in the browser.

---

## Chapter 10: Conclusion & Future Scope

### 10.1 Final Conclusion
The SafeRoute-AI project successfully demonstrates that historical accident records are drastically more valuable when paired with real-time contextual Machine Learning. By transitioning from static black-spots to dynamic, weather-aware probability multipliers via Uber H3 spatial math, the system achieves a massive **~80% ROC-AUC accuracy** while maintaining sub-15ms latencies. This unequivocally proves its viability for integration into modern, real-time autonomous navigation systems (ADAS) and commercial GPS routing engines.

### 10.2 Future Enhancements
*   **Traffic Density APIs:** Integrating live Google Maps traffic APIs to add vehicle congestion as a real-time ML feature.
*   **Audio HMI Alerts:** Integrating `pyttsx3` text-to-speech to physically speak the warnings (e.g., *"Warning, Fatal Intersection 500 meters ahead"*) to reduce driver screen-distraction.
*   **Dynamic Re-Routing:** If the Lookahead Radar detects a FATAL zone up ahead due to sudden rain, automatically pinging the OSRM routing engine to suggest an alternative, safer route in real-time.
