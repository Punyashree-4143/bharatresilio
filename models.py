from pydantic import BaseModel
from typing import List

class Action(BaseModel):
    action_type: str

class Observation(BaseModel):
    pending_orders: int
    available_riders: int
    failures: List[str]
    step_count: int

    system_health: float
    latency: int
    throughput: int

    latency_ms: int
    socket_health_index: float

    critical_failure: bool
    available_actions: List[str]