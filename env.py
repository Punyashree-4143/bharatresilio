import random
from models import Action, Observation
from chaos_engine import ChaosEngine

class BharatResilioEnv:

    def __init__(self, task="sprinter"):
        self.task = task
        self.reset()

    def reset(self):

        if self.task == "sprinter":
            orders = 5
            chaos_level = "easy"

        elif self.task == "flaky_network":
            orders = 10
            chaos_level = "medium"

        else:
            orders = 20
            chaos_level = "hard"

        self.chaos = ChaosEngine(level=chaos_level)

        self.state_data = {
            "pending_orders": orders,
            "available_riders": 3,
            "failures": [],
            "step_count": 0,
            "system_health": 1.0,
            "latency": 0,
            "throughput": 0,
            "completed_orders": 0,
            "budget": 10
        }

        self.last_action = None
        return self._get_obs()

    def state(self):
        return self.state_data

    # -------------------------
    # ACTIONS AVAILABLE
    # -------------------------
    def _get_available_actions(self):

        actions = ["DIAGNOSE_SYSTEM", "WAIT"]

        if self.state_data["available_riders"] > 0 and self.state_data["pending_orders"] > 0:
            actions.append("ASSIGN_RIDER")

        if self.state_data["available_riders"] == 0:
            actions.append("ADD_RIDER")

        if "API_TIMEOUT" in self.state_data["failures"]:
            actions.append("RETRY_API")

        if "DB_LATENCY" in self.state_data["failures"]:
            actions.append("SCALE_SYSTEM")

        if self.state_data["latency"] > 0:
            actions.append("PRIORITIZE_ORDERS")

        return actions

    # -------------------------
    # OBSERVATION (PARTIAL)
    # -------------------------
    def _get_obs(self):

        visible_failures = random.sample(
            self.state_data["failures"],
            k=min(2, len(self.state_data["failures"]))
        )

        return Observation(
            pending_orders=self.state_data["pending_orders"],
            available_riders=self.state_data["available_riders"],
            failures=visible_failures,
            step_count=self.state_data["step_count"],
            system_health=self.state_data["system_health"],
            latency=self.state_data["latency"],
            throughput=self.state_data["throughput"],
            latency_ms=self.state_data["latency"] * 100,
            socket_health_index=self.state_data["system_health"],
            critical_failure=len(self.state_data["failures"]) > 2,
            available_actions=self._get_available_actions()
        )

    # -------------------------
    # STEP FUNCTION
    # -------------------------
    def step(self, action: Action):

        self.state_data["step_count"] += 1

        # trigger chaos
        events = self.chaos.trigger()

        # ✅ LIMIT FAILURE GROWTH (CRITICAL FIX)
        self.state_data["failures"] = list(
            set(self.state_data["failures"]) | set(events)
        )
        if len(self.state_data["failures"]) > 4:
            self.state_data["failures"] = self.state_data["failures"][:4]

        reward = 0

        # -------------------------
        # ACTION LOGIC
        # -------------------------

        if action.action_type == "DIAGNOSE_SYSTEM":
            reward += 0.3 if len(self.state_data["failures"]) > 0 else -0.05

        elif action.action_type == "ASSIGN_RIDER":

            if self.state_data["available_riders"] > 0 and self.state_data["pending_orders"] > 0:

                if len(self.state_data["failures"]) >= 2:
                    reward -= 1.0   # 🔥 reduced penalty
                elif len(self.state_data["failures"]) == 1:
                    reward += 1.0
                else:
                    reward += 2.5   # 🔥 slightly higher reward

                self.state_data["pending_orders"] -= 1
                self.state_data["available_riders"] -= 1
                self.state_data["completed_orders"] += 1
                self.state_data["throughput"] += 1

            else:
                reward -= 0.5

        elif action.action_type == "ADD_RIDER":

            if self.state_data["budget"] > 0:
                self.state_data["available_riders"] += 1
                self.state_data["budget"] -= 1
                reward -= 0.2   # 🔥 less punishment
            else:
                reward -= 1.0

        elif action.action_type == "RETRY_API":

            if "API_TIMEOUT" in self.state_data["failures"] and "DB_LATENCY" not in self.state_data["failures"]:
                self.state_data["failures"].remove("API_TIMEOUT")
                reward += 0.8
            else:
                reward -= 0.05

        elif action.action_type == "SCALE_SYSTEM":

            if "DB_LATENCY" in self.state_data["failures"]:
                self.state_data["failures"].remove("DB_LATENCY")
                reward += 0.8
            else:
                reward -= 0.05

            self.state_data["system_health"] += 0.1

        elif action.action_type == "PRIORITIZE_ORDERS":
            self.state_data["latency"] = max(0, self.state_data["latency"] - 1)
            reward += 0.2

        elif action.action_type == "WAIT":
            reward -= 0.05

        # -------------------------
        # FAILURE EFFECTS
        # -------------------------

        if "DB_LATENCY" in self.state_data["failures"]:
            self.state_data["latency"] += 1   # 🔥 reduced impact
            self.state_data["system_health"] -= 0.1

        if "RIDER_SHORTAGE" in self.state_data["failures"]:
            self.state_data["available_riders"] = max(0, self.state_data["available_riders"] - 1)

        if "TRAFFIC_SPIKE" in self.state_data["failures"]:
            self.state_data["pending_orders"] += 1

        # -------------------------
        # 🔥 AUTO RECOVERY (CRITICAL)
        # -------------------------

        if len(self.state_data["failures"]) > 2:
            removed = random.choice(self.state_data["failures"])
            self.state_data["failures"].remove(removed)

        # -------------------------
        # CLEAN REWARD
        # -------------------------

        reward += (
            + 1.5 * self.state_data["completed_orders"]
            - 0.7 * len(self.state_data["failures"])
            - 0.03 * self.state_data["latency"]
        )

        # repetition penalty
        if self.last_action == action.action_type:
            reward -= 0.03

        self.last_action = action.action_type

        # bounds
        self.state_data["pending_orders"] = max(0, self.state_data["pending_orders"])
        self.state_data["system_health"] = max(0, min(1, self.state_data["system_health"]))

        # terminal
        done = (
            self.state_data["pending_orders"] == 0
            or self.state_data["step_count"] >= 20
        )

        error_msg = "|".join(self.state_data["failures"]) if self.state_data["failures"] else None

        return self._get_obs(), reward, done, {"error": error_msg}