from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float = Field(..., gt=0)
    timestamp: datetime
    currency: str = Field(default = "USD", min_length = 3, max_length = 3)

    @field_validator("currency")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.upper()

class SubgraphPayload(BaseModel):
    transaction_id: str
    user_id: str
    user_features: list[float]
    merchant_features: list[float]
    edge_features: list[float]

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
    created_at: datetime = Field(default_factory = datetime.utcnow)

class IngestResponse(BaseModel):
    accepted: bool
    transaction_id: str

class AlertAck(BaseModel):
    stored: bool
    transaction_id: str

NODE_FEATURE_NAMES = ['degree_norm', 'vel_1h_norm', 'vel_24h_norm', 'average_amount_norm']
EDGE_FEATURE_NAMES = ["amount_norm", "hour_norm", "is_weekend"]

def get_risk_band(score: float) -> str:
    if score < 0.3 :
        return "low"
    if score < 0.7:
        return "medium"
    return "high"
    