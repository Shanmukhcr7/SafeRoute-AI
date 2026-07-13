# config/risk_config.py

# Hybrid Risk Score Weights
RISK_WEIGHTS = {
    "HISTORICAL_DENSITY": 0.40,
    "FATALITY_RATE": 0.20,
    "ENVIRONMENTAL_RISK": 0.15,
    "ROAD_GEOMETRY": 0.10,
    "TIME_BASED_RISK": 0.05,
    "AI_PREDICTION": 0.10  # Initially 0 until XGBoost is trained
}

# Risk Level Thresholds
def get_risk_level(score: float):
    if score <= 20:
        return "Safe", "🟢"
    elif score <= 40:
        return "Low", "🟡"
    elif score <= 60:
        return "Moderate", "🟠"
    elif score <= 80:
        return "High", "🔴"
    else:
        return "Critical", "⚫"

# Weather Mappings (Assuming ATM variable in Kaggle Dataset)
# 1 = Normal, 2 = Light Rain, 3 = Heavy Rain, 4 = Snow, 5 = Fog, etc.
WEATHER_MAP = {
    1: 'Clear',
    2: 'Light Rain',
    3: 'Heavy Rain',
    4: 'Snow',
    5: 'Fog',
    6: 'Wind',
    7: 'Dazzling Sun',
    8: 'Cloudy',
    9: 'Other'
}
