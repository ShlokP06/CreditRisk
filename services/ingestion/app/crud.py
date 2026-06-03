from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Transaction


async def get_row_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Transaction))
    return result.scalar_one()


async def bulk_insert(db: AsyncSession, rows: list[dict], batch_size: int = 5000) -> None:
    for i in range(0, len(rows), batch_size):
        await db.execute(Transaction.__table__.insert(), rows[i : i + batch_size])
        await db.commit()


async def get_latest_for_user(db: AsyncSession, user_id: str) -> Transaction | None:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.transaction_dt.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def insert_live(db: AsyncSession, row: dict) -> None:
    db.add(Transaction(**row))
    await db.commit()
