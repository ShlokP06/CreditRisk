import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal, create_tables, get_db
from .schemas import Transaction, IngestResponse, EnrichmentResponse
from .crud import get_latest_for_user, insert_live
from .loader import load_csv_if_empty
from .metrics import received_total, metrics_response


async def _bg_load() -> None:
    async with AsyncSessionLocal() as db:
        await load_csv_if_empty(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    asyncio.create_task(_bg_load())
    yield


app = FastAPI(title="ingestion-service", lifespan=lifespan)


@app.post("/ingest", response_model=IngestResponse)
async def ingest(txn: Transaction, db: AsyncSession = Depends(get_db)):
    received_total.labels(status="accepted").inc()
    await insert_live(db, {
        "transaction_id": txn.transaction_id,
        "user_id": txn.user_id,
        "transaction_dt": int(txn.timestamp.timestamp()),
        "amount": txn.amount,
        "product_cd": txn.product_cd,
        "card4": txn.card_brand.lower(),
        "card6": txn.card_type.lower(),
        "p_emaildomain": txn.p_emaildomain,
        "addr1": txn.addr1 if txn.addr1 != -1.0 else None,
        "dist1": txn.dist1,
        "c1": txn.c1, "c2": txn.c2, "c6": txn.c6, "c13": txn.c13, "c14": txn.c14,
        "m1": txn.m1, "m2": txn.m2, "m3": txn.m3, "m4": txn.m4, "m5": txn.m5, "m6": txn.m6,
        "d1": txn.d1 if txn.d1 != -1.0 else None,
        "d4": txn.d4 if txn.d4 != -1.0 else None,
    })
    return IngestResponse(accepted=True, transaction_id=txn.transaction_id)


@app.get("/enrich/{user_id}", response_model=EnrichmentResponse)
async def enrich(user_id: str, db: AsyncSession = Depends(get_db)):
    row = await get_latest_for_user(db, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No history for user_id={user_id}")
    return EnrichmentResponse(
        user_id=user_id,
        found=True,
        p_emaildomain=row.p_emaildomain or "other",
        addr1=row.addr1 if row.addr1 is not None else -1.0,
        dist1=row.dist1 if row.dist1 is not None else 0.0,
        c1=row.c1 or 0.0,
        c2=row.c2 or 0.0,
        c6=row.c6 or 0.0,
        c13=row.c13 or 0.0,
        c14=row.c14 or 0.0,
        m1=row.m1 if row.m1 is not None else -1,
        m2=row.m2 if row.m2 is not None else -1,
        m3=row.m3 if row.m3 is not None else -1,
        m4=row.m4 if row.m4 is not None else -1,
        m5=row.m5 if row.m5 is not None else -1,
        m6=row.m6 if row.m6 is not None else -1,
        d1=row.d1 if row.d1 is not None else -1.0,
        d4=row.d4 if row.d4 is not None else -1.0,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return metrics_response()
