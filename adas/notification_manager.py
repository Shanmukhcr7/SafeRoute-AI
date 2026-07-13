import heapq
import time
import logging

class NotificationManager:
    """Manages an Alert Priority Queue for the ADAS system."""
    
    def __init__(self):
        self.queue = []
        
    def add_alert(self, alert_level: int, message: str, tte: float):
        """
        Adds an alert to the priority queue.
        Python heapq is a min-heap, so we negate the level to make it a max-heap (Priority 5 is highest).
        """
        # Format: (-level, timestamp, message, tte)
        # Timestamp ensures stable sorting if levels are equal
        heapq.heappush(self.queue, (-alert_level, time.time(), message, tte))
        
    def get_highest_priority_alert(self):
        """Returns and removes the highest priority alert from the queue."""
        if not self.queue:
            return None
        
        neg_level, timestamp, message, tte = heapq.heappop(self.queue)
        
        # Clear lower priority alerts if a critical one is popped to avoid spam
        # In a real car, you don't want 10 warnings right after an emergency.
        if -neg_level >= 4:
            self.queue.clear()
            
        return {
            "level": -neg_level,
            "message": message,
            "tte": tte,
            "timestamp": timestamp
        }
