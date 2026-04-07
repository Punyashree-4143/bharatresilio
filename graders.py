def _safe(score):
    """
    Force score safely inside (0,1)
    Avoid lower/upper edge values completely
    """
    return max(0.3, min(0.8, round(score, 2)))


def grade_sprinter(state):
    total = 10
    completed = total - state["pending_orders"]

    # smoothing to avoid 0 or 1
    score = (completed + 1) / (total + 2)
    return _safe(score)


def grade_flaky_network(state):
    total = 10
    completed = total - state["pending_orders"]

    # smoothing
    score = (completed + 1) / (total + 2)
    return _safe(score)


def grade_bharat_storm(state):
    total = 20
    completed = total - state["pending_orders"]

    # smoothing (critical)
    completion = (completed + 1) / (total + 2)

    health = state.get("system_health", 1)
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    score = 0.5 * completion + 0.3 * health + 0.2 * latency_penalty
    return _safe(score)