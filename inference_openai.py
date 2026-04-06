import os
from openai import OpenAI
from env import BharatResilioEnv
from models import Action
from graders import grade_bharat_storm

# 🔑 REQUIRED ENV VARIABLES (STRICT CHECK)
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

# OpenAI client (NO default token)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

env = BharatResilioEnv(task="bharat_storm")
obs = env.reset()

print("[START] task=bharat_storm env=bharatresilio model=openai-agent")

rewards = []
steps = 0

# 🔥 Helper: convert observation to text
def format_obs(obs):
    return f"""
Pending Orders: {obs.pending_orders}
Available Riders: {obs.available_riders}
Failures: {obs.failures}
Latency: {obs.latency}
System Health: {obs.system_health}
Available Actions: {obs.available_actions}
"""

# 🔥 Fallback rule-based (SAFE)
def fallback(obs):
    failures = set(obs.failures)

    if "DB_LATENCY" in failures:
        return "SCALE_SYSTEM"
    elif "API_TIMEOUT" in failures:
        return "RETRY_API"
    elif "TRAFFIC_SPIKE" in failures:
        return "PRIORITIZE_ORDERS"
    elif obs.available_riders == 0:
        return "ADD_RIDER"
    elif obs.pending_orders > 0:
        return "ASSIGN_RIDER"
    return "WAIT"


for _ in range(20):

    try:
        prompt = f"""
You are a logistics AI managing deliveries under failures.

Choose ONE action from:
ASSIGN_RIDER, ADD_RIDER, RETRY_API, SCALE_SYSTEM, PRIORITIZE_ORDERS, DIAGNOSE_SYSTEM, WAIT

Goal:
- Maximize deliveries
- Minimize failures and latency

Current State:
{format_obs(obs)}

Respond with ONLY the action name.
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,  # ✅ from env
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        action_str = response.choices[0].message.content.strip()

        # validate action
        if action_str not in obs.available_actions:
            action_str = fallback(obs)

    except Exception as e:
        print("API Error → using fallback:", e)
        action_str = fallback(obs)

    action = Action(action_type=action_str)

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