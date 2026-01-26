from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 9010

    # FlowShadow (ly_server)
    flowshadow_base_url: AnyUrl
    flowshadow_api_key: str = Field(min_length=1)

    # DeepSOC
    deepsoc_base_url: AnyUrl
    deepsoc_api_key: str = Field(min_length=1)

    # Sync
    sync_enabled: bool = True
    sync_interval_seconds: int = 10
    sync_batch_size: int = 200
    sync_lookback_seconds: int = 600
    sync_max_retries: int = 5

    # DB
    database_url: str = "sqlite:///./adapter.db"

    # Internal API auth
    adapter_internal_api_key: str = Field(min_length=1)

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
