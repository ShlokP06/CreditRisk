import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from .schemas import SubgraphPayload, ScoreResponse
from .config import settings
from .model import FraudModel
from .metrics import scoring_latency, predictions, model_info, metrics_response


@asynccontextmanager
async def lifespan(app):
    model = FraudModel.load(settings.model_path)
    app.state.model = model
    model_info.labels(version=model.version).set(1)
    yield


app = FastAPI(title="scoring-service", lifespan=lifespan)


@app.post("/score", response_model=ScoreResponse)
async def score(payload: SubgraphPayload, request: Request):
    model = request.app.state.model
    start = time.perf_counter()
    result = model.predict(payload)
    scoring_latency.observe(time.perf_counter() - start)
    predictions.labels(risk_band=result.risk_band).inc()
    return result


@app.get("/health")
async def health(request: Request):
    return {"status": "ok", "model": request.app.state.model.version}


@app.get("/metrics")
async def metrics():
    return metrics_response()
