from fastapi import APIRouter, Depends

from ..config import Settings, get_settings

router = APIRouter()


@router.get("/health")
def health(s: Settings = Depends(get_settings)):
    return {"status": "ok", "mode": s.gpc_mode}
