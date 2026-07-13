import time
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from simulation.vehicle_model import DigitalVehicle, DriverProfile
from simulation.route_engine import RouteEngine
from simulation.telemetry_logger import TelemetryLogger
from context.context_engine import ContextEngine
from context.dynamic_risk_engine import DynamicRiskEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SimulationManager:
    """Orchestrates the Digital Twin vehicles and the environment."""
    
    def __init__(self):
        self.vehicles = {}
        self.routes = {}
        self.logger = TelemetryLogger()
        self.context_engine = ContextEngine()
        self.risk_engine = DynamicRiskEngine()
        
    def add_vehicle(self, vehicle_id: str, profile: str, waypoints: list):
        logging.info(f"Adding Digital Twin {vehicle_id} ({profile}) to simulation.")
        self.vehicles[vehicle_id] = DigitalVehicle(vehicle_id, profile)
        self.routes[vehicle_id] = RouteEngine(waypoints)
        
    def step_simulation(self, dt_seconds: float = 1.0, environment: dict = None):
        """Advances the simulation by dt_seconds for all vehicles."""
        if environment is None:
            environment = {"rain": False, "fog": False, "snow": False, "hour": 12}
            
        for vid, vehicle in self.vehicles.items():
            route = self.routes[vid]
            
            if route.is_finished:
                if vehicle.state != "STOPPED":
                    logging.info(f"Vehicle {vid} reached destination.")
                    vehicle.state = "STOPPED"
                    vehicle.speed = 0.0
                    self.logger.log_telemetry(vehicle)
                continue
                
            # Move vehicle
            lat, lon, heading = route.advance_vehicle(vehicle.speed, dt_seconds)
            vehicle.update_telemetry(lat, lon, heading)
            
            # Combine Environment + Vehicle Telemetry into Context
            raw_data = environment.copy()
            raw_data.update({
                "lat": lat,
                "lon": lon,
                "speed": vehicle.speed,
                "heading": heading,
                "road_type": "Highway", # Placeholder, ideally mapped from GIS
                "is_curve": False
            })
            
            # Evaluate Context
            context_obj = self.context_engine.build_context(raw_data)
            
            # Calculate Risk
            risk_result = self.risk_engine.process_context(context_obj)
            
            # Update Vehicle Twin
            vehicle.update_risk_status(risk_result)
            
            # Log Telemetry for Playback Dashboard
            self.logger.log_telemetry(vehicle)
            
            # Minimal terminal output to show it's alive
            logging.info(f"[{vid}] {vehicle.state} | Spd: {vehicle.speed:.1f} | Zone: {vehicle.zone} | Risk: {vehicle.risk:.1f}")

if __name__ == "__main__":
    # Example standalone run
    sim = SimulationManager()
    
    # Simple route near Paris (Lat, Lon)
    route_a = [
        (48.8566, 2.3522),
        (48.8600, 2.3600),
        (48.8650, 2.3700)
    ]
    
    sim.add_vehicle("V-01", DriverProfile.NORMAL, route_a)
    sim.add_vehicle("V-02", DriverProfile.AGGRESSIVE, route_a)
    
    environment_conditions = {
        "rain": True,
        "fog": False,
        "snow": False,
        "hour": 22 # Night + Rain = High Risk
    }
    
    logging.info("Starting Simulation loop...")
    for _ in range(5): # Run 5 seconds of simulation
        sim.step_simulation(dt_seconds=1.0, environment=environment_conditions)
        time.sleep(1) # Simulate real-time tick
