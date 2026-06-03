import csv
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from .crud import bulk_insert, get_row_count
from .config import settings

logger = logging.getLogger(__name__)
_M = {"T": 1, "F": 0}


def _f(v: str | None) -> float | None:
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _m(v: str | None) -> int:
    return _M.get(v or "", -1)


async def load_csv_if_empty(db: AsyncSession) -> None:
    if await get_row_count(db) > 0:
        logger.info("DB already populated, skipping CSV load")
        return

    txn_path = Path(settings.transaction_csv_path)
    if not txn_path.exists():
        logger.warning("CSV not found at %s, starting with empty DB", txn_path)
        return

    identity: dict[str, str] = {}
    identity_path = Path(settings.identity_csv_path)
    if identity_path.exists():
        with open(identity_path, newline="") as f:
            for row in csv.DictReader(f):
                dt = (row.get("DeviceType") or "").lower()
                identity[row["TransactionID"]] = dt if dt else "unknown"

    logger.info("Loading %s into PostgreSQL...", txn_path)
    batch: list[dict] = []
    total = 0
    with open(txn_path, newline="") as f:
        for row in csv.DictReader(f):
            tid = row["TransactionID"]
            c1_raw = row.get("card1") or ""
            try:
                uid = str(int(float(c1_raw))) if c1_raw else "unknown"
            except ValueError:
                uid = "unknown"
            batch.append({
                "transaction_id": tid,
                "user_id": uid,
                "transaction_dt": int(float(row.get("TransactionDT") or 0)),
                "amount": float(row.get("TransactionAmt") or 0),
                "product_cd": row.get("ProductCD") or None,
                "card4": (row.get("card4") or "").lower() or None,
                "card6": (row.get("card6") or "").lower() or None,
                "p_emaildomain": row.get("P_emaildomain") or None,
                "addr1": _f(row.get("addr1")),
                "dist1": _f(row.get("dist1")),
                "c1": _f(row.get("C1")), "c2": _f(row.get("C2")),
                "c6": _f(row.get("C6")), "c13": _f(row.get("C13")), "c14": _f(row.get("C14")),
                "m1": _m(row.get("M1")), "m2": _m(row.get("M2")), "m3": _m(row.get("M3")),
                "m4": _m(row.get("M4")), "m5": _m(row.get("M5")), "m6": _m(row.get("M6")),
                "d1": _f(row.get("D1")), "d4": _f(row.get("D4")),
                "is_fraud": int(row["isFraud"]) if row.get("isFraud") else None,
                "device_type": identity.get(tid),
            })
            total += 1
            if len(batch) >= 5000:
                await bulk_insert(db, batch)
                logger.info("Inserted %d rows...", total)
                batch.clear()
    if batch:
        await bulk_insert(db, batch)
    logger.info("CSV load complete: %d rows", total)
