from fastapi import Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

scoring_latency = Histogram(
    "scoring_latency_seconds",
    "Time spent scoring a transaction subgraph",
)

predictions = Counter(
    "predictions_total",
    "Number of predictions made, labelled by risk band",
    ["risk_band"],
)

model_info = Gauge(
    "model_version_info",
    "Currently loaded model version",
    ["version"],
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
