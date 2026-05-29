from fastapi import Response
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

alerts_total = Counter(
    "alerts_triggered_total",
    "Total number of alerts triggered",
)

active_alerts = Gauge(
    "active_alerts",
    "Number of alerts currently held in the store",
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
