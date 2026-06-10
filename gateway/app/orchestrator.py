from fastapi import HTTPException
from .schemas import GatewayScoreResponse, EnrichedScoreResponse, Transaction

_ENRICHMENT_FIELDS = [
    "p_emaildomain", "addr1", "dist1",
    "c1", "c2", "c6", "c13", "c14",
    "m1", "m2", "m3", "m4", "m5", "m6",
    "d1", "d4",
]

_ENRICHMENT_DEFAULTS = {
    "p_emaildomain": "other",
    "addr1": -1.0, "dist1": 0.0,
    "c1": 0.0, "c2": 0.0, "c6": 0.0, "c13": 0.0, "c14": 0.0,
    "m1": -1, "m2": -1, "m3": -1, "m4": -1, "m5": -1, "m6": -1,
    "d1": -1.0, "d4": -1.0,
}


class Orchestrator:
    def __init__(self, client, settings):
        self.client = client
        self.settings = settings

    async def run(self, txn) -> GatewayScoreResponse:
        payload = await self.post(self.settings.feature_url + "/features", txn.model_dump(mode="json"))
        result = await self.post(self.settings.scoring_url + "/score", payload)
        alerted = False
        if result["risk_score"] > self.settings.alert_threshold:
            await self.post(self.settings.alert_url + "/alert", {
                "transaction_id": result["transaction_id"],
                "user_id": txn.user_id,
                "risk_score": result["risk_score"],
                "risk_band": result["risk_band"],
                "top_contributors": result["top_contributors"],
            })
            alerted = True
        return GatewayScoreResponse(**result, alerted=alerted)

    async def run_enriched(self, minimal) -> EnrichedScoreResponse:
        enrich_data, enriched = {}, False
        try:
            resp = await self.client.get(
                f"{self.settings.ingestion_url}/enrich/{minimal.user_id}", timeout=3.0
            )
            if resp.status_code == 200:
                enrich_data, enriched = resp.json(), True
        except Exception:
            pass

        txn_data = {
            "transaction_id": minimal.transaction_id,
            "user_id": minimal.user_id,
            "merchant_id": minimal.merchant_id,
            "amount": minimal.amount,
            "timestamp": minimal.timestamp.isoformat(),
            "currency": minimal.currency,
            "product_cd": minimal.product_cd,
            "card_brand": minimal.card_brand,
            "card_type": minimal.card_type,
            "device_type": minimal.device_type,
            **_ENRICHMENT_DEFAULTS,
        }
        if enriched:
            for field in _ENRICHMENT_FIELDS:
                val = enrich_data.get(field)
                if val is not None:
                    txn_data[field] = val

        txn = Transaction(**txn_data)
        result = await self.run(txn)
        return EnrichedScoreResponse(**result.model_dump(), enriched=enriched, user_known=enriched)

    async def post(self, url: str, data: dict) -> dict:
        try:
            resp = await self.client.post(url, json=data, timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
