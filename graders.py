def grade_sprinter(state):
    return 1.0 if state["pending_orders"] == 0 else 0.0


def grade_flaky_network(state):
    total = 10
    completed = total - state["pending_orders"]
    return round(completed / total, 2)


def grade_bharat_storm(state):
    total = 20
    completed = total - state["pending_orders"]

    completion = completed / total
    health = state.get("system_health", 1)
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    score = 0.5 * completion + 0.3 * health + 0.2 * latency_penalty
    return round(score, 2)