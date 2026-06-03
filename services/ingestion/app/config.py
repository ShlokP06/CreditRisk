from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://credit:credit@postgres:5432/credit_risk"
    transaction_csv_path: str = "/data/train_transaction.csv"
    identity_csv_path: str = "/data/train_identity.csv"


settings = Settings()
