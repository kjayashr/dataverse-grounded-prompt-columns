"""Config for live mode. Mock mode needs none of this."""
import os


class Config:
    def __init__(self, org_url=None, model_name=None, api_version="v9.2"):
        self.org_url = (org_url or os.environ.get("DATAVERSE_URL", "")).rstrip("/")
        self.model_name = model_name or os.environ.get("PROMPT_MODEL_NAME", "")
        self.api_version = api_version

    @property
    def api_base(self):
        return f"{self.org_url}/api/data/{self.api_version}"

    def require_live(self):
        if not self.org_url:
            raise SystemExit("Set DATAVERSE_URL (e.g. https://org406c2541.crm.dynamics.com) "
                             "or pass --org for live mode.")
