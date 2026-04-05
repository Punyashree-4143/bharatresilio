from env import BharatResilioEnv
from models import Action
from graders import grade_bharat_storm

env = BharatResilioEnv(task="bharat_storm")
obs = env.reset()

print("[START] task=bharat_storm env=bharatresilio model=final-pass-agent")

rewards = []
steps = 0

for step in range(20):

    failures = set(obs.failures)

    # =========================
    # 🔥 PHASE 1: EARLY DELIVERY (0–6 steps)
    # =========================
    if step < 6:
        if obs.available_riders == 0:
            action = Action(action_type="ADD_RIDER")
        else:
            action = Action(action_type="ASSIGN_RIDER")

    # =========================
    # 🔥 PHASE 2: CONTROL DAMAGE (6–20)
    # =========================
    else:

        # Fix only major issues
        if "DB_LATENCY" in failures:
            action = Action(action_type="SCALE_SYSTEM")

        elif "API_TIMEOUT" in failures:
            action = Action(action_type="RETRY_API")

        elif "TRAFFIC_SPIKE" in failures:
            action = Action(action_type="PRIORITIZE_ORDERS")

        # Add rider ONLY if none
        elif obs.available_riders == 0:
            action = Action(action_type="ADD_RIDER")

        # Deliver remaining orders
        elif obs.pending_orders > 3:
            action = Action(action_type="ASSIGN_RIDER")

        else:
            action = Action(action_type="WAIT")

    # STEP
    obs, reward, done, info = env.step(action)

    rewards.append(f"{reward:.2f}")
    steps += 1

    print(
        f"[STEP] step={steps} action={action.action_type} "
        f"reward={reward:.2f} done={str(done).lower()} error={info.get('error')}"
    )

    if done:
        break

print(f"[END] steps={steps} rewards={','.join(rewards)}")
print("Final Score:", grade_bharat_storm(env.state()))