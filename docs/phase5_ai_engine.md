# Phase 5: AI Prediction Engine

## Architectural Pivot
Instead of making the amateur mistake of training an AI model to predict a static, hard-coded risk score, Phase 5 introduces a robust **Severity Prediction Engine**.

The XGBoost/Random Forest models are trained purely on independent environmental, temporal, and road geometric variables (e.g., Rain, Night, Curve) to predict **Accident Severity** (Uninjured, Minor, Hospitalized, Fatal) completely agnostic of historical zone density.

## The Final Dynamic Risk Formula
```text
Final Dynamic Risk = Historical Risk (Density & Past Fatalities) 
                     * AI Severity Prediction Multiplier (Based on current conditions)
```
If a historically "Safe" road suddenly experiences Heavy Rain at Night, the AI will predict high severity, dynamically increasing the GIS Map's Risk Score to "High Risk" in real-time.

## Component Breakdown

1. **`dataset.py`**: Merges raw `users.csv` severity data (`grav`) with the environmental features from `processed_accidents` to create a clean, independent supervised learning dataset.
2. **`feature_selector.py`**: Employs Variance Thresholds, Correlation Elimination (<0.85), and Recursive Feature Elimination (RFE) to objectively filter noise.
3. **`trainer.py`**: Trains and aggressively compares `Random Forest`, `XGBoost`, and optionally `LightGBM`.
4. **`evaluator.py`**: Generates a massive JSON payload containing the Confusion Matrix, ROC/AUC curves, Precision/Recall, and Feature Importance.
5. **`model_registry.py`**: Professionally saves the best-performing model as a `.pkl` alongside a `metadata.json` file detailing accuracy, features, and versioning.
6. **`predictor.py`**: The API Gateway. Accepts a dictionary of current conditions, outputs the severity prediction, generates the SHAP explanation, and computes the Final Dynamic Risk.
7. **`shap_explainer.py`**: Emulates SHAP logic to extract the exact percentage contribution of features (e.g., `Rain +18%`, `Night +14%`) for the UI Popups.

## Next Phase Preview
With the Prediction API live, we will move into **Phase 6: Real-Time Weather Intelligence**, where we will ping live APIs and push the conditions into `predictor.py`, natively altering the colors on our Folium map dynamically.
