import logging
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ml.predictor import RiskPredictorAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DynamicRiskEngine:
    """Calculates Final Dynamic Risk, Forecasts, and Recommendations."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        self.predictor = RiskPredictorAPI()
        
    def get_historical_risk(self, h3_zone: str) -> float:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT risk_score FROM risk_scores WHERE h3_index = ?", (h3_zone,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 20.0 # Default Safe
        except Exception as e:
            logging.error(f"Error fetching historical risk: {e}")
            return 20.0
            
    def get_status(self, score: float) -> str:
        if score <= 20: return "SAFE"
        if score <= 40: return "WATCH"
        if score <= 60: return "WARNING"
        if score <= 80: return "DANGER"
        return "CRITICAL"
        
    def generate_recommendations(self, status: str, explanations: list) -> list:
        recs = []
        if status in ["DANGER", "CRITICAL"]:
            recs.append("Reduce Speed by 20 km/h immediately.")
            recs.append("Increase Following Distance.")
        elif status == "WARNING":
            recs.append("Monitor Road Conditions.")
            
        if any("Visibility" in e for e in explanations):
            recs.append("Turn On Headlights & Fog Lights.")
        if any("Grip" in e or "Ice" in e for e in explanations):
            recs.append("Avoid Sudden Braking.")
            
        if not recs:
            recs.append("Drive Normally.")
            
        return recs

    def process_context(self, context_obj: dict) -> dict:
        logging.info(f"Processing context for Zone {context_obj['h3_zone']}...")
        
        # 1. Historical Risk
        hist_risk = self.get_historical_risk(context_obj['h3_zone'])
        
        # 2. AI Severity Probability (From Phase 5)
        ai_result = self.predictor.predict(context_obj['raw_features'])
        ai_severity = ai_result.get('prediction', 'Safe')
        
        # Severity Multiplier
        sev_mult = {"Safe": 1.0, "Low Risk": 1.1, "Moderate Risk": 1.25, "High Risk": 1.5}.get(ai_severity, 1.0)
        
        # 3. Context Modifiers
        mods = context_obj['modifiers']
        total_modifier = mods['weather'] + mods['time'] + mods['road'] + mods['speed']
        
        # 4. Final Dynamic Risk Formula
        # Historical * AI Severity + Context Modifiers
        dynamic_risk = (hist_risk * sev_mult) + total_modifier
        dynamic_risk = min(dynamic_risk, 100.0)
        
        # 5. Calculate 5-Min Forecast (Simulated worsening/improving conditions based on speed/weather)
        # If it's raining and night, risk tends to compound
        forecast_risk = min(dynamic_risk * (1.1 if mods['weather'] > 0 else 0.95), 100.0)
        
        status = self.get_status(dynamic_risk)
        recs = self.generate_recommendations(status, context_obj['explanations'])
        
        result = {
            "h3_zone": context_obj['h3_zone'],
            "historical_risk": round(hist_risk, 1),
            "dynamic_risk": round(dynamic_risk, 1),
            "forecast_5min": round(forecast_risk, 1),
            "status": status,
            "ai_severity": ai_severity,
            "ai_confidence": ai_result.get('confidence', '0%'),
            "active_modifiers": context_obj['explanations'],
            "recommendations": recs
        }
        
        # Queue Alert if WARNING or worse
        if status in ["WARNING", "DANGER", "CRITICAL"]:
            self._queue_alert(result)
            
        return result
        
    def _queue_alert(self, result: dict):
        logging.info(f"Queueing {result['status']} Alert to Database...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alerts (vehicle, zone, risk, time, type) VALUES (?, ?, ?, datetime('now'), ?)",
                ("V-SIM", result['h3_zone'], result['dynamic_risk'], result['status'])
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to queue alert: {e}")
