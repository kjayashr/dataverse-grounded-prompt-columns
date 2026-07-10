from fastapi import APIRouter, Depends, HTTPException

from .. import mock
from ..config import Settings, get_settings

router = APIRouter(prefix="/api")


@router.get("/accounts")
async def accounts(s: Settings = Depends(get_settings)):
    """Grounded, cited Renewal Risk records. Snapshot in mock mode, live query otherwise."""
    if s.gpc_mode == "live":
        if not (s.azure_tenant_id and s.azure_client_id and s.azure_client_secret):
            raise HTTPException(500, "live mode needs AZURE_TENANT_ID / CLIENT_ID / CLIENT_SECRET")
        from ..dataverse import fetch_live
        try:
            data = await fetch_live(s)
        except Exception as e:  # surface Dataverse/auth errors clearly
            raise HTTPException(502, f"Dataverse query failed: {e}")
    else:
        data = mock.get_accounts(s.org_web_base)
    return {"mode": s.gpc_mode, "count": len(data), "accounts": data}
