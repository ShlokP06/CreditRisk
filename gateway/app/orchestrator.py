import httpx
from fastapi import HTTPException
from .schemas import GatewayScoreResponse

class Orchestrator:
    def __iniit__(self, client, settings):
        self.client = client
        self.settings = settings

    async def run(self, txn):
        payload = await self.post(self.settings.feature_url + "/features", txn.model_dump(mode = "json"))
        result = await self.post(self.settings.scoring_url + "/score", payload)
        alerted = False
        if result["risk_score"] > self.settings.alert_threshold:
            alert_body = {
                "transaction_id": result["transaction_id"],
                "user_id": txn.user_id,
                "risk_score": result["risk_score"],
                "risk_band": result["result_band"],
                "top_contributors": result["top_contributors"]
            }
            await self.post(self.settings.alert_url + "/alert", alert_body)
            alerted = True
        return GatewayScoreResponse(**result, alerted=alerted)
    
    async def post(self, url, data):
        try:
            resp = await self.client.post(url, json=data, timeout = 5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code = 502, detail=str(e))
        