import random
from models import Action, Observation
from chaos_engine import ChaosEngine
from graders import grade_sprinter, grade_flaky_network, grade_bharat_storm


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

    def _get_available_actions(self):
        actions = ["DIAGNOSE_SYSTEM", "WAIT"]

        if self.state_data["available_riders"] > 0 and self.state_data["pending_orders"] > 0:
            actions.append("ASSIGN_RIDER")

        if self.state_data["available_riders"] <= 1:
            actions.append("ADD_RIDER")

        if "API_TIMEOUT" in self.state_data["failures"]:
            actions.append("RETRY_API")

        if "DB_LATENCY" in self.state_data["failures"]:
            actions.append("SCALE_SYSTEM")

        if self.state_data["latency"] > 0:
            actions.append("PRIORITIZE_ORDERS")

        return actions

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
            available_actions=self._get_available_actions(),

            # Required fields
            latency_ms=int(self.state_data["latency"] * 100),
            socket_health_index=float(self.state_data["system_health"]),
            critical_failure=bool(len(self.state_data["failures"]) > 2)
        )

    def step(self, action: Action):
        self.state_data["step_count"] += 1

        # Chaos events
        events = self.chaos.trigger()
        self.state_data["failures"] = list(set(self.state_data["failures"]) | set(events))

        if len(self.state_data["failures"]) > 4:
            self.state_data["failures"] = self.state_data["failures"][:4]

        reward = 0.0
        atype = action.action_type

        # ----------------------------------
        # ACTION LOGIC
        # ----------------------------------
        if atype == "ASSIGN_RIDER":
            if self.state_data["available_riders"] > 0 and self.state_data["pending_orders"] > 0:
                reward += 2.0 if not self.state_data["failures"] else 0.5
                self.state_data["pending_orders"] -= 1
                self.state_data["available_riders"] -= 1
                self.state_data["completed_orders"] += 1
            else:
                reward -= 0.5

        elif atype == "RETRY_API":
            if "API_TIMEOUT" in self.state_data["failures"]:
                self.state_data["failures"].remove("API_TIMEOUT")
                reward += 1.0

        elif atype == "SCALE_SYSTEM":
            if "DB_LATENCY" in self.state_data["failures"]:
                self.state_data["failures"].remove("DB_LATENCY")
                reward += 1.0
            self.state_data["system_health"] = min(1.0, self.state_data["system_health"] + 0.2)

        elif atype == "WAIT":
            reward -= 0.05

        # ----------------------------------
        # GLOBAL REWARD SHAPING
        # ----------------------------------
        reward += (1.0 * self.state_data["completed_orders"])
        reward -= (0.5 * len(self.state_data["failures"]))

        self.last_action = atype

        # Normalize state
        self.state_data["pending_orders"] = max(0, self.state_data["pending_orders"])
        self.state_data["system_health"] = max(0.0, min(1.0, self.state_data["system_health"]))

        # Done condition
        done = (
            self.state_data["pending_orders"] == 0
            or self.state_data["step_count"] >= 20
        )

        # ----------------------------------
        # 🔥 NORMALIZE REWARD (CRITICAL)
        # ----------------------------------
        reward = max(0.02, min(0.98, float(reward) / 10.0))

        # ----------------------------------
        # INFO + FINAL SCORE
        # ----------------------------------
        info = {
            "error": "|".join(self.state_data["failures"]) if self.state_data["failures"] else None
        }

        if done:
            try:
                if self.task == "sprinter":
                    score = grade_sprinter(self.state_data)
                elif self.task == "flaky_network":
                    score = grade_flaky_network(self.state_data)
                else:
                    score = grade_bharat_storm(self.state_data)

                raw_val = float(score[0]) if isinstance(score, tuple) else float(score)

                # 🔥 STRICT SAFE RANGE (NO 0.01 / 0.99)
                info["score"] = max(0.02, min(0.98, raw_val))

            except Exception:
                info["score"] = 0.5

        return self._get_obs(), reward, done, info