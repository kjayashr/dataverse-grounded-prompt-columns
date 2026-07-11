from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import promptcol
from ..config import Settings, get_settings

router = APIRouter(prefix="/api")


class RunBody(BaseModel):
    mode: str = "advanced"
    instruction: str = ""
    tools: list[str] = []


@router.get("/promptcol/status")
def status(s: Settings = Depends(get_settings)):
    """Whether the functional Test is wired, plus the MCP tool catalog for the pop-up."""
    return {
        "enabled": s.llm_enabled,
        "deployment": s.aoai_deployment if s.llm_enabled else None,
        "tools": promptcol.TOOLS,
    }


@router.post("/promptcol/run")
def run(body: RunBody, s: Settings = Depends(get_settings)):
    """Run the real instruction through gpt-4.1 and return answer + real citations + trace."""
    if not s.llm_enabled:
        raise HTTPException(503, "Model not configured (set AOAI_ENDPOINT / AOAI_KEY).")
    mode = body.mode if body.mode in ("default", "advanced") else "advanced"
    try:
        return promptcol.run(s, mode, body.instruction, body.tools)
    except Exception as e:  # surface upstream errors to the pop-up rather than 500-ing opaquely
        raise HTTPException(502, f"Model call failed: {e}")
