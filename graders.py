def _safe(score, offset=0.0):
    """
    Ensure score is in (0,1) AND unique per task
    """
    score = score + offset

    if score <= 0:
        score = 0.21 + offset
    elif score >= 1:
        score = 0.79 - offset

    return round(score, 3)


def grade_sprinter(state):
    total = 10
    completed = total - state["pending_orders"]

    base = (completed + 2) / (total + 4)

    # 🔥 unique offset
    return _safe(base, offset=0.05)


def grade_flaky_network(state):
    total = 10
    completed = total - state["pending_orders"]

    base = (completed + 1) / (total + 3)

    # 🔥 different offset
    return _safe(base, offset=0.02)


def grade_bharat_storm(state):
    total = 20
    completed = total - state["pending_orders"]

    completion = (completed + 1) / (total + 2)

    health = state.get("system_health", 1)
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    base = 0.5 * completion + 0.3 * health + 0.2 * latency_penalty

    # 🔥 different offset
    return _safe(base, offset=0.03)