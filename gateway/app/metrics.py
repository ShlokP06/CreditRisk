from fastapi import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

pipeline_latency = Histogram(
    "gateway_pipeline_latency_seconds",
    "End to end latency of the scoring pipeline through the gateway",
)

pipeline_errors = Counter(
    "pipeline_errors_total",
    "Errors hit while orchestrating the pipeline, labelled by stage",
    ["stage"],
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
