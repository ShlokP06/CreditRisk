from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    feature_url: str = "http://feature:8002"
    scoring_url: str = "http://scoring:8003"
    alert_url: str = "http://alert:8004"
    alert_threshold: float = 0.7


settings = Settings()
