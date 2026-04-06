---
title: BharatResilio
emoji: 🌩️
colorFrom: blue
colorTo: purple
sdk: docker
app_file: inference.py
pinned: false
---
# 🌩️ BharatResilio: Hyperlocal Logistics Resilience Gym

BharatResilio is a chaos-driven reinforcement learning environment designed to train AI agents in **logistics orchestration under unreliable infrastructure**.

Inspired by real-world Indian systems like ONDC, Swiggy, and Zomato, the environment simulates cascading failures such as API timeouts, database latency, and rider shortages.

---

## 🚀 Core Innovation

Unlike traditional logistics simulators, BharatResilio introduces **Adversarial System Dynamics**, where the agent must manage both:

- 📦 Delivery operations  
- ⚙️ Infrastructure health  

### Key Features

- **Event-Driven Chaos**: API failures, DB latency, traffic spikes  
- **Resource Constraints**: Trade-off between cost and efficiency  
- **Partial Observability**: Limited visibility of failures  
- **Causal Dependencies**: DB issues → API failures → delivery delays  

---

## 👁️ Observation Space

The agent receives a structured state including:

- `pending_orders` – number of deliveries remaining  
- `available_riders` – active delivery agents  
- `failures` – partial system failure signals  
- `system_health` – infrastructure stability score  
- `latency` – system delay  
- `throughput` – completed deliveries  

---

## 🎮 Action Space

| Action | Category | Description |
|------|--------|------------|
| ASSIGN_RIDER | Business | Assign delivery to rider |
| ADD_RIDER | Logistics | Increase fleet size (costly) |
| RETRY_API | Infrastructure | Resolve API failures |
| SCALE_SYSTEM | Infrastructure | Fix DB latency |
| PRIORITIZE_ORDERS | Strategy | Reduce latency |
| DIAGNOSE_SYSTEM | Observability | Inspect system |
| WAIT | Strategy | Do nothing |

---

## 🎯 Task Curriculum

| Task | Difficulty | Description |
|------|----------|------------|
| sprinter | Easy | Minimal chaos, optimize speed |
| flaky_network | Medium | Intermittent API failures |
| bharat_storm | Hard | Severe cascading failures |

---

## 🧠 Reward Function

The environment provides **dense rewards**:

- ✅ Positive reward for successful deliveries  
- ❌ Penalties for failures and inefficiency  
- ⚠️ Penalizes incorrect actions (e.g., delivering during failures)  
- 🎯 Encourages infrastructure-first decision making  

---

## 🤖 Baseline Agents

### 🔹 Rule-Based Agent

```bash
python inference.py
Deterministic
Stable performance
Used for reproducible baseline
🔹 OpenAI-Based Agent
python inference_openai.py
Uses OpenAI API (OPENAI_API_KEY)
Model: gpt-4o-mini
Falls back to rule-based policy if API is unavailable
Demonstrates LLM-driven decision making
📊 Performance
Average Score: ~0.2 – 0.3
Best Score: 0.44

Due to stochastic chaos and partial observability, results vary across runs.
Evaluation is based on average performance rather than a single run.

🐳 Run with Docker
docker build -t bharatresilio .
docker run bharatresilio
⚙️ Setup (Local)
pip install -r requirements.txt
python inference.py
📦 OpenEnv Compliance

This environment fully implements the OpenEnv specification:

step(action) → returns observation, reward, done, info
reset() → initializes environment
state() → returns internal state
Typed models using Pydantic
openenv.yaml configuration
🏗️ Architecture

BharatResilio bridges web systems + reinforcement learning:

Backend Simulation: Event-driven chaos engine
RL Interface: Python-based OpenEnv wrapper
State Tracking: Real-time system + logistics metrics

---
### 👥 Developed by Team BharatResilio
**Punyashree** | *Final Year MCA* | 📍 Bengaluru, India  
**Nikhil** | *2nd Year Engineering* | 📍 Bengaluru, India  

*A collaborative project focused on High-Availability Logistics and Reinforcement Learning Orchestration.*


