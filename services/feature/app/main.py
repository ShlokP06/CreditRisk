import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from .schemas import Transaction, FeatureVector
from .features import FeatureEngine
from .metrics import extraction_latency, graph_size, metrics_response

@asynccontextmanager
async def lifespan(app):
    app.state.engine = FeatureEngine()
    yield

app = FastAPI(title="feature-service", lifespan=lifespan)

@app.post("/features", response_model=FeatureVector)
async def features(txn: Transaction, request: Request):
    engine = request.app.state.engine
    start = time.perf_counter()
    payload = await engine.extract(txn)
    extraction_latency.observe(time.perf_counter() - start)
    graph_size.set(len(engine.user_tx_counts))
    return payload

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return metrics_response()

