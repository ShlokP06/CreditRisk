from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    model_path: str = "/app/model/model.pkl"
    model_fallback: str = ""
    alert_threshold: float = 0.7


settings = Settings()
