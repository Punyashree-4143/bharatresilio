FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# install fastapi + server
RUN pip install fastapi uvicorn

EXPOSE 7860

# ✅ run API server
CMD ["sh", "-c", "python inference.py & uvicorn server.app:app --host 0.0.0.0 --port 7860"]