from fastapi import FastAPI

from .schemas import Transaction, IngestResponse
from .metrics import received_total, metrics_response

app = FastAPI(title="ingestion-service")


@app.post("/ingest", response_model=IngestResponse)
async def ingest(txn: Transaction):
    received_total.labels(status="accepted").inc()
    return IngestResponse(accepted=True, transaction_id=txn.transaction_id)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return metrics_response()
