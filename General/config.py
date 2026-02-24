from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Environment Context ---
    environment: str = "development"

    # --- Database Configurations ---
    database_url: str

    # --- Kafka Configurations ---
    kafka_broker_url: str
    kafka_broker_port: int

    # --- API Servers ---
    external_api_port: int
    internal_api_port: int

    # --- Worker / Model Services ---
    tinybert_worker_port: int
    xgboost_worker_port: int

    KAFKA_CONTAINER_NAME: str
    EXTERNAL_API_URL: str
    INTERNAL_API_URL: str

    # Pydantic Config: Tells it to look for the .env file in the root directory
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignores any extra variables in the .env file we don't map here
    )


# Instantiate the settings object.
# This reads the .env file once when the app starts.
settings = Settings()
