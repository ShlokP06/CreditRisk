import joblib
import numpy as np
import shap

from .schemas import FeatureVector, ScoreResponse, FeatureContributor, get_risk_band
from .config import settings


class DummyModel:
    version = "dummy-v0"

    def predict(self, payload: FeatureVector) -> ScoreResponse:
        return ScoreResponse(
            transaction_id=payload.transaction_id,
            risk_score=0.5,
            risk_band="medium",
            model_version=self.version,
            top_contributors=[],
        )


class FraudModel:
    def __init__(self):
        self.model = None
        self.explainer = None
        self.feature_names: list[str] = []
        self.threshold: float = 0.5
        self.version: str = "unknown"

    @classmethod
    def load(cls, path: str):
        if settings.model_fallback:
            return DummyModel()
        artifact = joblib.load(path)
        inst = cls()
        inst.model = artifact["model"]
        inst.explainer = shap.TreeExplainer(artifact["model"])
        inst.feature_names = artifact["feature_names"]
        inst.threshold = artifact["threshold"]
        inst.version = artifact["version"]
        return inst

    def predict(self, payload: FeatureVector) -> ScoreResponse:
        x = np.array(payload.features, dtype=np.float32).reshape(1, -1)
        score = float(self.model.predict_proba(x)[0, 1])

        shap_vals = self.explainer(x)
        attributions = shap_vals.values[0].tolist()

        ranked = sorted(
            zip(self.feature_names, attributions, payload.features),
            key=lambda t: abs(t[1]),
            reverse=True,
        )
        top3 = [
            FeatureContributor(feature=f, attribution=round(a, 4), feature_value=round(v, 4))
            for f, a, v in ranked[:3]
        ]

        return ScoreResponse(
            transaction_id=payload.transaction_id,
            risk_score=round(score, 4),
            risk_band=get_risk_band(score),
            model_version=self.version,
            top_contributors=top3,
        )
