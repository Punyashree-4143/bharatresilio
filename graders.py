def grade_easy(state):
    return 1.0 if state["pending_orders"] == 0 else 0.0


def grade_medium(state):
    total = 5
    completed = total - state["pending_orders"]
    return round(completed / total, 2)


def grade_hard(state):
    total = 8
    completed = total - state["pending_orders"]
    completion = completed / total

    system_health = state.get("system_health", 1)

    return round(completion * system_health, 2)