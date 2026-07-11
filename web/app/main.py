"""Grounded Prompt Columns web service.

Serves the Dynamics-themed UI and the /api/accounts endpoint (snapshot in mock
mode, live Dataverse when configured). Deploys to Azure Container Apps; see
deploy/deploy.sh.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import accounts, health, promptcol, semantic

settings = get_settings()
app = FastAPI(title="Grounded Prompt Columns", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_cache(request, call_next):
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    return resp


app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(semantic.router)
app.include_router(promptcol.router)

# Serve the UI last so /health and /api/* take precedence.
_static = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=_static, html=True), name="static")
