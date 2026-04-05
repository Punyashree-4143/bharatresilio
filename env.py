from models import Action, Observation
from chaos_engine import ChaosEngine

class BharatResilioEnv:

    def __init__(self, task="medium"):
        self.task = task
        self.chaos = ChaosEngine(level=task)
        self.reset()

    def reset(self):

        if self.task == "easy":
            orders = 2
        elif self.task == "medium":
            orders = 5
        else:
            orders = 8

        self.state = {
            "pending_orders": orders,
            "available_riders": 3,
            "failures": [],
            "step_count": 0,

            # system metrics
            "system_health": 1.0,
            "latency": 0,
            "throughput": 0,
            "completed_orders": 0
        }

        self.last_action = None

        return self._get_obs()

    def _get_obs(self):
        return Observation(
            pending_orders=self.state["pending_orders"],
            available_riders=self.state["available_riders"],
            failures=self.state["failures"],
            step_count=self.state["step_count"],
            system_health=self.state["system_health"],
            latency=self.state["latency"],
            throughput=self.state["throughput"]
        )

    def step(self, action: Action):

        self.state["step_count"] += 1

        # Trigger chaos
        events = self.chaos.trigger()
        self.state["failures"] = events

        reward = 0

        # =====================
        # ACTIONS
        # =====================

        if action.action_type == "ASSIGN_RIDER":
            if self.state["available_riders"] > 0 and self.state["pending_orders"] > 0:
                self.state["pending_orders"] -= 1
                self.state["available_riders"] -= 1
                self.state["completed_orders"] += 1
                self.state["throughput"] += 1
                reward += 2.0   # 🔥 STRONG DELIVERY REWARD
            else:
                reward -= 1.0

        elif action.action_type == "ADD_RIDER":
            self.state["available_riders"] += 1
            reward -= 0.2

        elif action.action_type == "RETRY_API":
            if "API_TIMEOUT" in events:
                reward += 0.5
            else:
                reward -= 0.1

        elif action.action_type == "SCALE_SYSTEM":
            self.state["system_health"] += 0.1
            reward -= 0.3

        elif action.action_type == "PRIORITIZE_ORDERS":
            if self.state["pending_orders"] > 0:
                self.state["latency"] = max(0, self.state["latency"] - 1)
                reward += 0.02   # 🔥 REDUCED IMPACT
            else:
                reward -= 0.3

        elif action.action_type == "WAIT":
            reward -= 0.05

        # =====================
        # FAILURE EFFECTS
        # =====================

        if "DB_LATENCY" in events:
            self.state["latency"] += 2
            self.state["system_health"] -= 0.2
            reward -= 0.3

        if "API_TIMEOUT" in events:
            reward -= 0.2

        if "RIDER_SHORTAGE" in events:
            self.state["available_riders"] = max(0, self.state["available_riders"] - 1)
            reward -= 0.3

        if "RIDER_CANCELLED" in events:
            reward -= 0.2

        if "TRAFFIC_SPIKE" in events:
            self.state["pending_orders"] += 1
            reward -= 0.2

        # =====================
        # STATE SAFETY
        # =====================

        self.state["pending_orders"] = max(0, self.state["pending_orders"])
        self.state["system_health"] = max(0, min(1, self.state["system_health"]))

        # =====================
        # MULTI-OBJECTIVE REWARD
        # =====================

        reward += self.state["system_health"] * 0.2
        reward -= self.state["latency"] * 0.05

        # Encourage real work
        reward += self.state["completed_orders"] * 0.1
        reward += self.state["throughput"] * 0.05

        # Penalize repetition
        if self.last_action == action.action_type:
            reward -= 0.1

        self.last_action = action.action_type

        # 🔥 Penalize pending work
        if self.state["pending_orders"] > 0:
            reward -= 0.1 * self.state["pending_orders"]

        # 🔥 Completion bonus
        if self.state["pending_orders"] == 0:
            reward += 5.0

        # Step penalty
        reward -= 0.05

        done = self.state["pending_orders"] <= 0 or self.state["step_count"] >= 20

        return self._get_obs(), reward, done, {}

    def state(self):
        return self.state