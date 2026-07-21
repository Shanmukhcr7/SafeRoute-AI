# Research Paper Draft: SafeRoute-AI

**Title:** SafeRoute-AI: Dynamic Road Accident Risk Zone Detection and Real-Time ADAS Alert System Using Geospatial Clustering and Machine Learning

**Authors:** Navadeep, Inderneel, Rithik Teja, Shanmukh (Guide: Dr./Mr. Ravi Krishna)

**Abstract:** 
Traditional road safety systems and Advanced Driver Assistance Systems (ADAS) heavily rely on static historical data to define accident "black-spots". However, road danger is inherently dynamic and severely influenced by transient environmental conditions such as weather, lighting, and time of day. This paper proposes SafeRoute-AI, a novel methodology that bridges static historical geospatial data with real-time environmental context. By utilizing 15 years of French accident records (220,000+ points), the system employs Uber’s H3 Hexagonal Hierarchical Spatial Index for ultra-low latency spatial hashing (`O(1)`) and a HistGradientBoosting Classifier for dynamic risk multipliers. To eliminate spatial target leakage, a "Macro-Region" coordinate rounding technique is introduced. Evaluated against a live simulated environment, SafeRoute-AI achieves a Receiver Operating Characteristic Area Under Curve (ROC-AUC) score of 0.795 and sub-15ms alert latency, proving its viability for proactive, real-time autonomous navigation systems.

**Keywords:** Advanced Driver Assistance Systems (ADAS), Machine Learning, Geospatial Clustering, Uber H3, Road Safety, HistGradientBoosting, Target Leakage.

---

### I. Introduction
Road traffic injuries are a leading cause of preventable mortality globally. While modern GPS routing engines heavily optimize for temporal efficiency (shortest path), they lack sophisticated real-time safety integration. Existing hotspot identification relies heavily on static heuristics—authorities mark specific intersections as dangerous based on historical volume. This approach fails to account for the dynamic nature of vehicular risk; an intersection may be statistically safe on a clear afternoon but highly lethal during nocturnal rain. 
This research proposes a paradigm shift from static maps to a dynamic "Digital Twin" simulator. SafeRoute-AI evaluates historical risk baselines and mathematically escalates or de-escalates that risk based on real-time environmental APIs, delivering proactive alerts to drivers before they enter an escalating hazard zone.

### II. Literature Review
Prior research into spatial accident prediction frequently utilizes density-based clustering algorithms such as DBSCAN or K-Means. While mathematically sound for finding geographic centers, these algorithms require costly distance matrix calculations (`O(N*K)` latency), rendering them unsuitable for high-speed, real-time ADAS applications.
Furthermore, modern fleet management safety systems rely on in-vehicle telematics hardware (OBD2 scanners) to monitor harsh braking. While accurate, these systems are hardware-dependent and financially inaccessible to the general public.
SafeRoute-AI bridges these gaps by removing hardware dependency entirely (relying solely on standard GPS) and utilizing hierarchical spatial hashing to drop latency to ~5 milliseconds, making it deployable on any standard mobile device or dashboard display.

### III. Proposed System

#### A. System Overview
SafeRoute-AI operates on a dual-pipeline architecture. The offline pipeline cleanses and spatially indexes historical accidents into a lightweight SQLite database while training a supervised Machine Learning model on environmental conditions. The online pipeline acts as a driver interface, tracking live vehicular GPS, querying the historical database, and applying the ML model to generate dynamic, contextual danger alerts via a 500-meter lookahead radar.

#### B. Dataset
The system is trained and validated on the "Accidents in France from 2005 to 2016" dataset sourced from Kaggle. This comprehensive governmental database includes `caracteristics.csv` (lighting, weather, atmospheric conditions, coordinates) and `users.csv` (injury gravity for individuals).

#### C. Data Preprocessing
Extensive geospatial normalization was required:
1. **Coordinate Multiplier Anomalies:** GPS coordinates logged without floating-point decimals by historical police terminals (e.g., `488566`) were mathematically divided by `100000` to restore geographical integrity.
2. **Bounds Filtering:** The dataset was strictly isolated to the French mainland (`lat` 41-52, `long` -6 to 10), removing overseas territories to preserve spatial continuity.
3. **Target Aggregation:** Individual injuries were grouped by unique Accident IDs (`Num_Acc`); the highest severity injury dictated the ultimate classification of the crash (Severe vs. Moderate).

#### D. Feature Engineering & Target Leakage Prevention
A significant challenge in spatial Machine Learning is "Target Leakage," where models simply memorize granular GPS coordinates instead of learning environmental causality. 
To counteract this, SafeRoute-AI engineers **"Macro-Regions"**. Granular `lat` and `long` coordinates are mathematically rounded to 1 decimal place (approx. 11x11 km grids). This forces the algorithm to understand overarching regional danger trends rather than memorizing micro-intersections, restoring the predictive weight of environmental features (`is_raining`, `is_night`, `hour`).

#### E. Machine Learning Model
The system utilizes Scikit-Learn’s `HistGradientBoostingClassifier`. Selected for its native handling of missing (NaN) values and exceptional training speed on large datasets (220,000+ records), the algorithm generates highly calibrated probability outputs (`predict_proba`) crucial for real-time risk scaling.

#### F. Risk Prediction Algorithm
The final risk score of a given spatial hexagon is a fusion of its historical base score and the ML Dynamic Multiplier. The ML model outputs the current probability of a severe accident. This is divided by the national baseline probability (55%) to create a scalar multiplier. If weather deteriorates, the multiplier heavily inflates the base historical risk, potentially upgrading a "MODERATE" zone to a "FATAL" zone in real-time.

### IV. System Architecture
The software architecture heavily isolates offline training from online inference:
1. **Data Layer:** SQLite3 stores pre-calculated Uber H3 Resolution-8 base risk scores.
2. **Inference Layer:** An optimized Python class loads the serialized `dynamic_risk_model.pkl` and constructs Pandas DataFrames in real-time to compute the weather multiplier.
3. **Simulation Layer:** A Streamlit frontend wrapped around a custom HTML/Javascript engine (Leaflet.js + Turf.js). Turf.js performs linear interpolation on OSRM geometries to simulate 60 FPS vehicular movement and rotational bearings.

### V. Implementation
The implementation relies entirely on a lightweight Python 3.10 stack. Uber's `h3-py` library is utilized for spatial indexing. Because H3 uses a deterministic string hash (e.g., `88184c...`), the system bypasses the computationally expensive Haversine distance formula, checking for hazard zone entry via instant hash-map lookups. This implementation guarantees that the 500m Lookahead Radar executes flawlessly on lightweight CPU environments.

### VI. Experimental Results
SafeRoute-AI was benchmarked against traditional static models using a 20% validation split.
* **Accuracy & ROC-AUC:** By implementing Macro-Regions, the model successfully avoids spatial target leakage and achieves a robust **0.795 ROC-AUC score**.
* **Alert Latency:** Compared to K-Means clustering (approx. 48ms latency), the proposed H3 string-matching algorithm operates at **~5ms latency** per step, effortlessly supporting the strict real-time constraints required by ADAS systems.
* **Feature Importance:** Permutation importance confirmed that environmental factors (`hour`, `is_night`, `is_raining`) actively drive the real-time predictions, validating the dynamic nature of the model.

### VII. Discussion
The results unequivocally demonstrate that static hotspot mapping is an archaic method of risk analysis. By mathematically fusing static baselines with dynamic Machine Learning probabilities, SafeRoute-AI successfully proves that historical data is significantly more valuable when contextualized. The reliance on Macro-Regions successfully solved the target leakage dilemma without sacrificing geographical region-specific trends.

### VIII. Conclusion
This paper presented SafeRoute-AI, a novel, real-time ADAS alert framework. By abandoning computationally expensive distance clustering in favor of Uber's H3 hierarchical indexing and applying a HistGradientBoosting contextual multiplier, the system successfully predicts and alerts drivers to escalating road hazards dynamically. With a ~80% ROC-AUC accuracy and sub-15ms latencies, it provides a highly accessible, hardware-free alternative to modern telematics systems.

### Future Work
Future iterations of this architecture will aim to integrate real-time traffic density APIs (e.g., Google Maps Traffic) to append vehicular congestion as a dynamic ML feature. Furthermore, the integration of an audio-based Human-Machine Interface (HMI) using Text-To-Speech engines would significantly reduce visual distraction, allowing drivers to receive proactive hazard warnings audibly.

### References
[1] "Road accident prediction and model interpretation using a hybrid k-means and random forest algorithm approach," *SN Applied Sciences*, vol. 2, pp. 1–13, 2020.
[2] "Estimation of road accident risk with machine learning," Ph.D. dissertation, Concordia University, 2020.
[3] "A Machine Learning Approach for Classifying Road Accident Hotspots," *ISPRS International Journal of Geo-Information*, vol. 12, no. 6, art. 227, 2023.
[4] "Predicting errors in accident hotspots and investigating spatiotemporal, weather, and behavioral factors using interpretable machine learning," *PLOS ONE*, 2025.
[5] A. Lahlou, "Accidents in France from 2005 to 2016," Kaggle Dataset, 2017. [Online]. Available: https://www.kaggle.com/datasets/ahmedlahlou/accidents-in-france-from-2005-to-2016
