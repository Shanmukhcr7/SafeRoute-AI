import random

class DriverProfile:
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"

class DigitalVehicle:
    """Digital Twin representing a vehicle in the simulation."""
    
    def __init__(self, vehicle_id: str, profile: str = DriverProfile.NORMAL):
        self.vehicle_id = vehicle_id
        self.profile = profile
        self.state = "IDLE"  # IDLE, MOVING, WARNING, DANGER, STOPPED
        
        # Telemetry
        self.lat = 0.0
        self.lon = 0.0
        self.speed = 0.0
        self.heading = 0.0
        self.zone = "UNKNOWN"
        self.risk = 0.0
        self.forecast = 0.0
        self.alerts = []
        
        # Determine base speed characteristics based on profile
        if self.profile == DriverProfile.SAFE:
            self.target_speed = random.uniform(40, 60)
        elif self.profile == DriverProfile.NORMAL:
            self.target_speed = random.uniform(50, 80)
        elif self.profile == DriverProfile.AGGRESSIVE:
            self.target_speed = random.uniform(80, 120)
            
    def update_telemetry(self, lat: float, lon: float, heading: float):
        self.lat = lat
        self.lon = lon
        self.heading = heading
        
        # Add slight variation to speed to simulate human driving
        variation = random.uniform(-5, 5)
        self.speed = max(0.0, self.target_speed + variation)
        
        if self.speed > 0 and self.state == "IDLE":
            self.state = "MOVING"
            
    def update_risk_status(self, risk_data: dict):
        self.zone = risk_data.get('h3_zone', self.zone)
        self.risk = risk_data.get('dynamic_risk', self.risk)
        self.forecast = risk_data.get('forecast_5min', self.forecast)
        
        status = risk_data.get('status', 'SAFE')
        if status in ["WARNING", "DANGER", "CRITICAL"]:
            self.state = status
            self.alerts.extend(risk_data.get('recommendations', []))
        else:
            self.state = "MOVING"
            self.alerts = []
