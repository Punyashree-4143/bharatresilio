import random

class ChaosEngine:

    def __init__(self, level="medium"):
        self.level = level

    def trigger(self):
        events = []

        if random.random() < 0.3:
            events.append("DB_LATENCY")

        if random.random() < 0.2:
            events.append("RIDER_SHORTAGE")

        # causal chain
        if "DB_LATENCY" in events:
            events.append("API_TIMEOUT")

        if "RIDER_SHORTAGE" in events:
            events.append("RIDER_CANCELLED")

        if random.random() < 0.2:
            events.append("TRAFFIC_SPIKE")

        return events  # ✅ FIXED (no comma)