from collections import deque

from fastapi import FastAPI

from .schemas import Alert, AlertAck
from .config import settings
from .narrator import narrate
from .metrics import alerts_total, active_alerts, metrics_response

store = deque(maxlen=settings.store_max)

app = FastAPI(title="alert-service")


@app.post("/alert", response_model=AlertAck)
async def create_alert(payload: Alert):
    stored = False
    if payload.risk_score > settings.alert_threshold:
        payload.narration = await narrate(payload)
        store.append(payload)
        alerts_total.inc()
        active_alerts.set(len(store))
        stored = True
    return AlertAck(stored=stored, transaction_id=payload.transaction_id)


@app.get("/alerts", response_model=list[Alert])
async def get_alerts(limit: int = 50):
    return list(store)[-limit:][::-1]


@app.get("/health")
async def health():
    return {"status": "ok", "alerts_stored": len(store)}


@app.get("/metrics")
async def metrics():
    return metrics_response()
