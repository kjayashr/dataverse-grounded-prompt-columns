from fastapi import APIRouter, Depends

from .. import semantic
from ..config import Settings, get_settings

router = APIRouter(prefix="/api")


@router.get("/semantic")
def semantic_demo(s: Settings = Depends(get_settings)):
    """Three-tier grounding contrast (keyword vs relationship vs semantic) for the hero account."""
    return semantic.get_semantic(s.org_web_base)
