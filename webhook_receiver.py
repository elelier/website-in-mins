from fastapi import FastAPI, Request
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="Webhook Receiver")

# Almacena los eventos recibidos para pruebas
received_events = []

@app.post("/webhook")
async def receive_webhook(request: Request):
    """Recibe y registra las notificaciones webhook"""
    event = await request.json()
    print(f"\n[{datetime.now()}] Webhook recibido:")
    print(json.dumps(event, indent=2, default=str))
    received_events.append(event)
    return {"status": "ok"}

@app.get("/events")
async def list_events():
    """Lista todos los eventos recibidos"""
    return received_events

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
