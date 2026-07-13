import math

class RouteEngine:
    """Handles smooth interpolation of GPS coordinates along a predefined route."""
    
    def __init__(self, waypoints: list):
        """waypoints: list of (lat, lon) tuples."""
        self.waypoints = waypoints
        self.current_leg = 0
        self.progress = 0.0 # 0.0 to 1.0 along the current leg
        self.is_finished = False
        
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        # Haversine formula (approximate)
        R = 6371.0 # Earth radius in km
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
        
    def _calculate_heading(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing

    def advance_vehicle(self, speed_kmh: float, dt_seconds: float = 1.0) -> tuple:
        """Moves the vehicle forward by dt seconds at speed_kmh."""
        if self.is_finished or self.current_leg >= len(self.waypoints) - 1:
            self.is_finished = True
            return self.waypoints[-1][0], self.waypoints[-1][1], 0.0
            
        p1 = self.waypoints[self.current_leg]
        p2 = self.waypoints[self.current_leg + 1]
        
        leg_distance_km = self._calculate_distance(p1[0], p1[1], p2[0], p2[1])
        if leg_distance_km == 0:
            self.current_leg += 1
            return p1[0], p1[1], 0.0
            
        distance_to_move_km = speed_kmh * (dt_seconds / 3600.0)
        
        # Calculate progress step
        progress_step = distance_to_move_km / leg_distance_km
        self.progress += progress_step
        
        if self.progress >= 1.0:
            # Reached next waypoint
            self.progress = 0.0
            self.current_leg += 1
            if self.current_leg >= len(self.waypoints) - 1:
                self.is_finished = True
                return p2[0], p2[1], 0.0
            p1 = self.waypoints[self.current_leg]
            p2 = self.waypoints[self.current_leg + 1]
            heading = self._calculate_heading(p1[0], p1[1], p2[0], p2[1])
            return p1[0], p1[1], heading
            
        # Linear Interpolation for lat/lon
        lat = p1[0] + (p2[0] - p1[0]) * self.progress
        lon = p1[1] + (p2[1] - p1[1]) * self.progress
        heading = self._calculate_heading(p1[0], p1[1], p2[0], p2[1])
        
        return lat, lon, heading
