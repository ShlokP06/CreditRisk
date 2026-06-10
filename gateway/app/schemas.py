from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="Card identifier (masked card number)")
    merchant_id: str = Field(..., description="Merchant identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    timestamp: datetime = Field(..., description="Transaction timestamp (ISO 8601)")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="ISO 4217 currency code")
    product_cd: str = Field(default="W", description="Product type: W=physical goods, H=hotel, C=cash, S=service, R=refund")
    card_brand: str = Field(default="visa", description="Card network: visa, mastercard, american express, discover")
    card_type: str = Field(default="credit", description="Card category: credit or debit")
    p_emaildomain: str = Field(default="other", description="Purchaser email domain (e.g. gmail.com, anonymous.com)")
    device_type: str = Field(default="unknown", description="Device used for transaction: desktop, mobile, or unknown")
    m1: int = Field(default=-1, description="Name on card matches billing name: 1=yes, 0=no, -1=unchecked")
    m2: int = Field(default=-1, description="Billing address matches card address: 1=yes, 0=no, -1=unchecked")
    m3: int = Field(default=-1, description="Billing address verified: 1=yes, 0=no, -1=unchecked")
    m4: int = Field(default=-1, description="Device fingerprint match: 1=yes, 0=no, -1=unchecked")
    m5: int = Field(default=-1, description="Shipping matches billing address: 1=yes, 0=no, -1=unchecked")
    m6: int = Field(default=-1, description="Billing address linked to known fraud: 1=yes, 0=no, -1=unchecked")
    addr1: float = Field(default=-1.0, description="Billing zip/postal code (-1 if unknown)")
    dist1: float = Field(default=0.0, description="Distance between billing and shipping address (0 if same)")
    c1: float = Field(default=0.0, description="Number of billing addresses linked to this card")
    c2: float = Field(default=0.0, description="Number of phone numbers linked to this card")
    c6: float = Field(default=0.0, description="Number of phone numbers on the billing address")
    c13: float = Field(default=0.0, description="Number of payment accounts sharing this email")
    c14: float = Field(default=0.0, description="Account transaction history depth")
    d1: float = Field(default=-1.0, description="Days since previous transaction (-1 if first transaction)")
    d4: float = Field(default=-1.0, description="Days since previous transaction alternate window (-1 if unknown)")

    @field_validator("currency")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.upper()


class FeatureVector(BaseModel):
    transaction_id: str
    user_id: str
    features: list[float]


class FeatureContributor(BaseModel):
    feature: str
    attribution: float
    feature_value: float


class ScoreResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_band: str
    model_version: str
    top_contributors: list[FeatureContributor]


class GatewayScoreResponse(ScoreResponse):
    alerted: bool


class Alert(BaseModel):
    transaction_id: str
    user_id: str
    risk_score: float
    risk_band: str
    top_contributors: list[FeatureContributor]
    narration: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IngestResponse(BaseModel):
    accepted: bool
    transaction_id: str


class AlertAck(BaseModel):
    stored: bool
    transaction_id: str


FEATURE_NAMES = [
    "amount_norm", "amount_log", "hour",
    "product_cd", "card_brand", "card_type", "p_email_bin",
    "m1", "m2", "m3", "m4", "m5", "m6",
    "device_type", "user_tx_count",
    "addr1", "dist1",
    "c1", "c2", "c6", "c13", "c14",
    "d1", "d4",
]


def get_risk_band(score: float) -> str:
    if score < 0.3:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


class MinimalTransaction(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)
    transaction_id: str = Field(default_factory=lambda: uuid4().hex[:16])
    merchant_id: str = "merchant_demo"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    product_cd: str = "W"
    card_brand: str = "visa"
    card_type: str = "credit"
    device_type: str = "unknown"
    currency: str = "USD"


class EnrichedScoreResponse(GatewayScoreResponse):
    enriched: bool
    user_known: bool
