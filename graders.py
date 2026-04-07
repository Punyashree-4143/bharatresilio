def _safe(score):
    """
    GUARANTEE score strictly between (0,1)
    """
    # hard clamp inside safe zone
    return max(0.31, min(0.79, round(score, 3)))


def grade_sprinter(state):
    total = 10
    completed = total - state["pending_orders"]

    # smoothing prevents 0 or 1
    score = (completed + 1) / (total + 2)
    return _safe(score)


def grade_flaky_network(state):
    total = 10
    completed = total - state["pending_orders"]

    score = (completed + 1) / (total + 2)
    return _safe(score)


def grade_bharat_storm(state):
    total = 20
    completed = total - state["pending_orders"]

    # smoothing → NEVER 0 or 1
    completion = (completed + 1) / (total + 2)

    health = state.get("system_health", 1)
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    score = 0.5 * completion + 0.3 * health + 0.2 * latency_penalty

    return _safe(score)