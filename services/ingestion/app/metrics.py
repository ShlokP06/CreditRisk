from fastapi import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

received_total = Counter(
    "transactions_received_total",
    "Total transactions received at ingestion",
    ["status"],
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
