import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.risk_config import RISK_WEIGHTS, get_risk_level

class RiskEngine:
    """Calculates the Hybrid Risk Score based on configuration weights."""
    
    def __init__(self, zone_stats: pd.DataFrame):
        self.zone_stats = zone_stats

    def calculate_hybrid_score(self) -> pd.DataFrame:
        """
        Calculates Risk Score:
        Final Risk Score = 40% Historical Accident Density + 20% Fatality Rate + 
        15% Environmental Risk + 10% Road Geometry + 5% Time-Based Risk + 10% AI Model.
        """
        df = self.zone_stats.copy()
        
        # Ensure normalization handles NaNs
        df = df.fillna(0)
        
        # Calculate component scores (assuming they are already 0-100 normalized where applicable)
        # We will use raw percentage columns directly if they are already 0-100 (e.g. rain_percentage)
        # For counts, they should have been normalized by `normalization.py` in the pipeline
        
        df['risk_score'] = (
            (df['norm_accident_count'] * RISK_WEIGHTS["HISTORICAL_DENSITY"]) +
            (df['norm_fatal_count'] * RISK_WEIGHTS["FATALITY_RATE"]) +
            (df['rain_percentage'] * RISK_WEIGHTS["ENVIRONMENTAL_RISK"]) +
            (df['curve_percentage'] * RISK_WEIGHTS["ROAD_GEOMETRY"]) +
            (df['night_percentage'] * RISK_WEIGHTS["TIME_BASED_RISK"]) +
            (0.0 * RISK_WEIGHTS["AI_PREDICTION"]) # Placeholder for XGBoost
        )
        
        # Cap at 100
        df['risk_score'] = df['risk_score'].clip(upper=100)
        
        # Apply Risk Levels & Colors
        df[['risk_level', 'risk_color']] = df['risk_score'].apply(
            lambda x: pd.Series(get_risk_level(x))
        )
        
        return df

    def generate_explanations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generates the 'Why is this zone dangerous?' explanation string."""
        explanations = []
        for _, row in df.iterrows():
            reasons = []
            if row['rain_percentage'] > 30:
                reasons.append(f"Heavy Rain ({row['rain_percentage']:.0f}%)")
            if row['curve_percentage'] > 30:
                reasons.append("Sharp Curves")
            if row['fatal_count'] > 0:
                reasons.append(f"High Fatality History")
            if row['night_percentage'] > 50:
                reasons.append(f"Night Accidents ({row['night_percentage']:.0f}%)")
            
            if not reasons:
                explanations.append("Historically Safe Zone")
            else:
                explanations.append(" • " + "\n • ".join(reasons))
                
        df['explanation'] = explanations
        return df
