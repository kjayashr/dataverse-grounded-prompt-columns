"""Settings, pydantic BaseSettings from a shared .env (matches the team convention)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "mock" serves the captured snapshot (no org needed). "live" queries Dataverse.
    gpc_mode: str = "mock"

    # Live mode: the org and a client-credentials app registration.
    dataverse_url: str = "https://org406c2541.crm.dynamics.com"
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # How many accounts to pull in live mode.
    account_top: int = 12

    # Azure OpenAI, for the functional prompt-column Test (real generation + citations).
    # Set AOAI_KEY as a Container App secret; never commit it.
    aoai_endpoint: str = ""
    aoai_key: str = ""
    aoai_deployment: str = "gpt-4.1"
    aoai_api_version: str = "2024-10-21"

    cors_origins: str = "*"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.aoai_endpoint and self.aoai_key)

    @property
    def org_web_base(self) -> str:
        """Base for citation deep-links to real records."""
        return self.dataverse_url.rstrip("/") + "/main.aspx?pagetype=entityrecord&etn="

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
