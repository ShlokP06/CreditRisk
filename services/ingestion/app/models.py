from sqlalchemy import BigInteger, Float, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(20), nullable=False)
    user_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    transaction_dt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    product_cd: Mapped[str | None] = mapped_column(String(4))
    card4: Mapped[str | None] = mapped_column(String(30))
    card6: Mapped[str | None] = mapped_column(String(20))
    p_emaildomain: Mapped[str | None] = mapped_column(String(100))
    addr1: Mapped[float | None] = mapped_column(Float)
    dist1: Mapped[float | None] = mapped_column(Float)
    c1: Mapped[float | None] = mapped_column(Float)
    c2: Mapped[float | None] = mapped_column(Float)
    c6: Mapped[float | None] = mapped_column(Float)
    c13: Mapped[float | None] = mapped_column(Float)
    c14: Mapped[float | None] = mapped_column(Float)
    m1: Mapped[int | None] = mapped_column(Integer)
    m2: Mapped[int | None] = mapped_column(Integer)
    m3: Mapped[int | None] = mapped_column(Integer)
    m4: Mapped[int | None] = mapped_column(Integer)
    m5: Mapped[int | None] = mapped_column(Integer)
    m6: Mapped[int | None] = mapped_column(Integer)
    d1: Mapped[float | None] = mapped_column(Float)
    d4: Mapped[float | None] = mapped_column(Float)
    is_fraud: Mapped[int | None] = mapped_column(SmallInteger)
    device_type: Mapped[str | None] = mapped_column(String(20))
