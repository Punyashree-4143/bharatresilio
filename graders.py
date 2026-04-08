# graders.py

def _safe(score):
    """
    OpenEnv Phase 2 requires scores strictly within (0, 1).
    This function forces the score into a safe 0.15 - 0.85 range.
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.5
        
    score = round(score, 2)

    # 🔥 FORCE SAFE RANGE
    if score <= 0.1:
        score = 0.15
    elif score >= 0.9:
        score = 0.85

    return score

def grade_sprinter(state):
    total = 5
    completed = state.get("completed_orders", 0)
    # Basic ratio: (completed / total)
    base = (completed) / (total) if total > 0 else 0
    return _safe(base + 0.10)

def grade_flaky_network(state):
    total = 10
    completed = state.get("completed_orders", 0)
    base = (completed) / (total) if total > 0 else 0
    return _safe(base + 0.05)

def grade_bharat_storm(state):
    total = 20
    completed = state.get("completed_orders", 0)
    
    # 1. Completion ratio
    completion = (completed) / (total) if total > 0 else 0
    
    # 2. System Health
    health = state.get("system_health", 1.0)
    
    # 3. Latency (Normalized: 0 is good, 20 is bad)
    latency_penalty = max(0, 1 - state.get("latency", 0) / 20)

    # Weighted Score
    base = (0.5 * completion) + (0.3 * health) + (0.2 * latency_penalty)
    
    # ✅ FIXED: No trailing comma. Returns a float.
    return _safe(base + 0.07)