from fastapi import Response
from prometheus_client import Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

extraction_latency = Histogram(
    "feature_extraction_latency_seconds",
    "Time spent extracting subgraph features per transaction",
)

graph_size = Gauge(
    "graph_nodes_total",
    "Number of nodes currently in the transaction graph",
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
