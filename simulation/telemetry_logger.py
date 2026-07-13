import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TelemetryLogger:
    """Logs Digital Twin telemetry to SQLite for Mission Control Playback."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        
    def log_telemetry(self, vehicle):
        """Logs the state of a DigitalVehicle."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO vehicle_telemetry 
                   (vehicle_id, timestamp, latitude, longitude, speed, heading, risk, zone, status) 
                   VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""",
                (
                    vehicle.vehicle_id,
                    vehicle.lat,
                    vehicle.lon,
                    vehicle.speed,
                    vehicle.heading,
                    vehicle.risk,
                    vehicle.zone,
                    vehicle.state
                )
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error logging telemetry for {vehicle.vehicle_id}: {e}")
