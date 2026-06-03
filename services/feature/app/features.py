import asyncio
import math

from .schemas import FeatureVector


PRODUCT_MAP = {"W": 0, "H": 1, "C": 2, "S": 3, "R": 4}
BRAND_MAP = {"visa": 0, "mastercard": 1, "american express": 2, "discover": 3}
TYPE_MAP = {"credit": 0, "debit": 1}
EMAIL_MAP = {
    "gmail.com": 0, "yahoo.com": 1,
    "hotmail.com": 2, "outlook.com": 2,
    "anonymous.com": 3,
}
DEVICE_MAP = {"desktop": 0, "mobile": 1}


class RunningStats:
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, x: float) -> None:
        self.count += 1
        delta = x - self.mean
        self.mean += delta / self.count
        delta2 = x - self.mean
        self.m2 += delta * delta2

    def normalize(self, x: float) -> float:
        if self.count < 2:
            return 0.0
        std = math.sqrt(self.m2 / self.count)
        return (x - self.mean) / (std + 1e-8)


class FeatureEngine:
    def __init__(self):
        self.amount_stats = RunningStats()
        self.user_tx_counts: dict[str, int] = {}
        self.lock = asyncio.Lock()

    async def extract(self, txn) -> FeatureVector:
        async with self.lock:
            self.amount_stats.update(txn.amount)
            self.user_tx_counts[txn.user_id] = self.user_tx_counts.get(txn.user_id, 0) + 1

            amount_norm = self.amount_stats.normalize(txn.amount)

            features = [
                amount_norm,
                math.log1p(txn.amount),
                float(txn.timestamp.hour),
                float(PRODUCT_MAP.get(txn.product_cd.upper(), -1)),
                float(BRAND_MAP.get(txn.card_brand.lower(), -1)),
                float(TYPE_MAP.get(txn.card_type.lower(), -1)),
                float(EMAIL_MAP.get(txn.p_emaildomain.lower(), 4)),
                float(txn.m1),
                float(txn.m2),
                float(txn.m3),
                float(txn.m4),
                float(txn.m5),
                float(txn.m6),
                float(DEVICE_MAP.get(txn.device_type.lower(), -1)),
                float(self.user_tx_counts[txn.user_id]),
                float(txn.addr1),
                math.log1p(max(txn.dist1, 0.0)),
                math.log1p(max(txn.c1, 0.0)),
                math.log1p(max(txn.c2, 0.0)),
                math.log1p(max(txn.c6, 0.0)),
                math.log1p(max(txn.c13, 0.0)),
                math.log1p(max(txn.c14, 0.0)),
                float(txn.d1),
                float(txn.d4),
            ]

            return FeatureVector(
                transaction_id=txn.transaction_id,
                user_id=txn.user_id,
                features=features,
            )
