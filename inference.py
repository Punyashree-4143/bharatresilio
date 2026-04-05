from env import BharatResilioEnv
from models import Action

env = BharatResilioEnv(task="medium")
obs = env.reset()

print("[START] task=chaos_survival env=bharatresilio model=final-agent")

rewards = []
steps = 0
done = False

for i in range(20):

    # 🔥 PRIORITY-BASED DECISION MAKING

    # 1. Fix critical failures first
    if "API_TIMEOUT" in obs.failures:
        action = Action(action_type="RETRY_API")

    elif "DB_LATENCY" in obs.failures:
        action = Action(action_type="SCALE_SYSTEM")

    # 2. Ensure resources
    elif obs.available_riders == 0:
        action = Action(action_type="ADD_RIDER")

    # 3. MAIN GOAL: Deliver orders
    elif obs.pending_orders > 0:
        action = Action(action_type="ASSIGN_RIDER")

    # 4. Optimization (only when no urgent work)
    elif obs.latency > 2:
        action = Action(action_type="PRIORITIZE_ORDERS")

    else:
        action = Action(action_type="WAIT")

    obs, reward, done, _ = env.step(action)

    reward_str = f"{reward:.2f}"
    rewards.append(reward_str)
    steps += 1

    print(
        f"[STEP] step={steps} action={action.action_type} "
        f"reward={reward_str} done={str(done).lower()} error=null"
    )

    if done:
        break

print(
    f"[END] success={str(done).lower()} "
    f"steps={steps} rewards={','.join(rewards)}"
)