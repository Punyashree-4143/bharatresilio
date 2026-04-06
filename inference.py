import os
from env import BharatResilioEnv
from models import Action
from graders import grade_bharat_storm

# 🔑 REQUIRED ENV VARIABLES (for checklist compliance)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")  # ⚠️ no default

env = BharatResilioEnv(task="bharat_storm")
obs = env.reset()

print("[START] task=bharat_storm env=bharatresilio model=smart-v2")

rewards = []
steps = 0

# 🔥 MEMORY
failure_memory = {}
add_rider_count = 0

for step in range(20):

    failures = set(obs.failures)

    # -------------------------
    # 🔥 UPDATE MEMORY
    # -------------------------
    for f in failures:
        failure_memory[f] = failure_memory.get(f, 0) + 1

    # decay memory
    for f in list(failure_memory.keys()):
        if f not in failures:
            failure_memory[f] -= 1
            if failure_memory[f] <= 0:
                del failure_memory[f]

    # -------------------------
    # 🔥 DECISION LOGIC
    # -------------------------

    # 1. Fix persistent DB issue
    if failure_memory.get("DB_LATENCY", 0) >= 1:
        action = Action(action_type="SCALE_SYSTEM")

    # 2. Fix API only if stable DB
    elif "API_TIMEOUT" in failures:
        action = Action(action_type="RETRY_API")

    # 3. Handle traffic smartly
    elif "TRAFFIC_SPIKE" in failures and obs.latency > 0:
        action = Action(action_type="PRIORITIZE_ORDERS")

    # 4. ADD RIDER (LIMITED)
    elif obs.available_riders == 0 and add_rider_count < 3 and obs.pending_orders > 2:
        action = Action(action_type="ADD_RIDER")
        add_rider_count += 1

    # 🔥 5. ALWAYS DELIVER (CORE BOOST)
    elif obs.pending_orders > 0 and obs.available_riders > 0:
        action = Action(action_type="ASSIGN_RIDER")

    # fallback
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