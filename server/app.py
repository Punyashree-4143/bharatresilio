from fastapi import FastAPI
from env import BharatResilioEnv
from models import Action

app = FastAPI()
env = BharatResilioEnv(task="bharat_storm")

@app.post("/reset")
def reset():
    return env.reset().dict()

@app.post("/step")
def step(action: dict):
    act = Action(**action)
    obs, reward, done, info = env.step(act)

    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/")
def home():
    return {"message": "BharatResilio server running 🚀"}