# graders.py

def _safe(score):
    """
    Ensures score is strictly within (0,1)
    and always returns a float.
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 0.5

    # 🔥 HARD SAFE RANGE
    if score <= 0.1:
        return 0.2
    if score >= 0.9:
        return 0.8

    return score


def grade_sprinter(state):
    total = 5
    completed = state.get("completed_orders", 0)

    base = (completed / total) if total > 0 else 0
    return _safe(base + 0.10)


def grade_flaky_network(state):
    total = 10
    completed = state.get("completed_orders", 0)

    base = (completed / total) if total > 0 else 0
    return _safe(base + 0.05)


def grade_bharat_storm(state):
    total = 20
    completed = state.get("completed_orders", 0)

    completion = (completed / total) if total > 0 else 0
    health = float(state.get("system_health", 1.0))
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    base = (0.5 * completion) + (0.3 * health) + (0.2 * latency_penalty)

    # ✅ IMPORTANT: NO TRAILING COMMA
    return _safe(base + 0.07)