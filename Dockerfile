FROM python:3.8-slim

WORKDIR /app

COPY . .

# Install dependencies (very minimal + stable)
RUN pip install --no-cache-dir fastapi uvicorn openai pydantic openenv-core

CMD ["sh", "-c", "python inference.py & uvicorn server.app:app --host 0.0.0.0 --port 7860"]