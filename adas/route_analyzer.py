import sqlite3
import h3
import math
from pathlib import Path
from adas.ml_predictor import DynamicRiskPredictor

class RouteAnalyzer:
    def __init__(self, db_path=None):
        if db_path is None:
            candidates = [
                Path(__file__).resolve().parent.parent / "database" / "road_risk.db",
                Path("database/road_risk.db"),
                Path("road-risk-ai/database/road_risk.db"),
            ]
            self.db_path = next((c for c in candidates if c.exists()), Path("database/road_risk.db"))
        else:
            self.db_path = Path(db_path)
            
        self.risk_zones = self._load_risk_zones()
        self.ml = DynamicRiskPredictor()
        
    def _load_risk_zones(self):
        if not self.db_path.exists():
            return {}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT h3_index, risk_score, risk_level, risk_color FROM risk_scores")
            rows = cursor.fetchall()
            return {r[0]: {"score": r[1], "level": r[2], "color": r[3]} for r in rows}
        except:
            return {}
        finally:
            conn.close()
            
    def analyze_route(self, route_geometry, weather="Clear", time_of_day="Day"):
        """
        Analyzes route against risk zones and applies ML dynamic multipliers.
        """
        print(f"Analyzing route dynamically for {weather} at {time_of_day}...")
        passed_zones = set()
        for i in range(0, len(route_geometry), 2): 
            pt = route_geometry[i]
            h3_idx = h3.latlng_to_cell(pt[1], pt[0], 8) 
            if h3_idx in self.risk_zones:
                passed_zones.add(h3_idx)
            # Include corridor neighbors with historical risk
            for neighbor in h3.grid_disk(h3_idx, 1):
                if neighbor in self.risk_zones and self.risk_zones[neighbor]["score"] >= 30:
                    passed_zones.add(neighbor)
                
        # Calculate dynamic score using ML model
        total_dynamic_score = 0
        max_risk = 0
        critical_count = 0
        
        # Deep copy to not permanently mutate the base zones
        dynamic_zones = {}
        
        for z in passed_zones:
            base_score = self.risk_zones[z]["score"]
            lat, lon = h3.cell_to_latlng(z)
            
            # Use ML model to predict danger based on weather, time, and location
            multiplier = self.ml.get_risk_multiplier(lat, lon, weather, time_of_day)
            
            # Calculate dynamic severity
            dynamic_score = min(base_score * multiplier, 100.0)
            
            # Recalculate level based on new score
            if dynamic_score >= 80: 
                level = "FATAL"
                dyn_color = "#DC2626"
            elif dynamic_score >= 65: 
                level = "CRITICAL"
                dyn_color = "#EF4444"
            elif dynamic_score >= 45: 
                level = "HIGH"
                dyn_color = "#F97316"
            elif dynamic_score >= 25: 
                level = "MODERATE"
                dyn_color = "#FBBF24"
            else: 
                level = "LOW"
                dyn_color = "#10B981"
            
            if level in ["CRITICAL", "FATAL"]:
                critical_count += 1
                
            dynamic_zones[z] = {
                "score": dynamic_score,
                "base_score": base_score,
                "multiplier": multiplier,
                "level": level,
                "color": dyn_color # Dynamically calculated so weather changes color
            }
            
            total_dynamic_score += dynamic_score
            max_risk = max(max_risk, dynamic_score)
            
        avg_risk = total_dynamic_score / len(passed_zones) if passed_zones else 0
        
        # Calculate AI Navigation Score (0-100, where 100 is perfectly safe)
        # Penalize heavily for critical zones and high average risk
        safety_score = 100 - (avg_risk * 0.5) - (critical_count * 5)
        safety_score = max(0, min(100, safety_score))
        
        return {
            "avg_risk": round(avg_risk, 1),
            "max_risk": round(max_risk, 1),
            "critical_zones": critical_count,
            "safety_score": round(safety_score, 1),
            "passed_zones": list(passed_zones),
            "dynamic_zones": dynamic_zones
        }
