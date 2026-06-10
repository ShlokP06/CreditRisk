import time
import asyncio
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Transaction, GatewayScoreResponse, MinimalTransaction, EnrichedScoreResponse
from .config import settings
from .orchestrator import Orchestrator
from .metrics import pipeline_latency, pipeline_errors, metrics_response


@asynccontextmanager
async def lifespan(app):
    client = httpx.AsyncClient()
    app.state.client = client
    app.state.orchestrator = Orchestrator(client, settings)
    yield
    await client.aclose()


app = FastAPI(title="api-gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/score", response_model=GatewayScoreResponse)
async def score(txn: Transaction, request: Request):
    orchestrator = request.app.state.orchestrator
    start = time.perf_counter()
    try:
        result = await orchestrator.run(txn)
    except HTTPException as e:
        pipeline_errors.labels(stage="pipeline").inc()
        raise e
    pipeline_latency.observe(time.perf_counter() - start)
    return result


@app.post("/score-enriched", response_model=EnrichedScoreResponse)
async def score_enriched(txn: MinimalTransaction, request: Request):
    orchestrator = request.app.state.orchestrator
    start = time.perf_counter()
    try:
        result = await orchestrator.run_enriched(txn)
    except HTTPException as e:
        pipeline_errors.labels(stage="pipeline").inc()
        raise e
    pipeline_latency.observe(time.perf_counter() - start)
    return result


@app.get("/health")
async def health(request: Request):
    client = request.app.state.client

    async def check(url: str) -> str:
        try:
            resp = await client.get(url + "/health", timeout=3.0)
            resp.raise_for_status()
            return "ok"
        except Exception:
            return "down"

    feature, scoring, alert, ingestion = await asyncio.gather(
        check(settings.feature_url),
        check(settings.scoring_url),
        check(settings.alert_url),
        check(settings.ingestion_url),
    )
    healthy = all(s == "ok" for s in (feature, scoring, alert))
    return {
        "gateway": "ok",
        "feature": feature,
        "scoring": scoring,
        "alert": alert,
        "ingestion": ingestion,
        "healthy": healthy,
    }


@app.get("/alerts")
async def alerts(request: Request, limit: int = 50):
    client = request.app.state.client
    try:
        resp = await client.get(settings.alert_url + "/alerts", params={"limit": limit}, timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/metrics")
async def metrics():
    return metrics_response()
