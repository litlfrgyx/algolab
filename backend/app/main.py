"""FastAPI aplikácia, vstupný bod backendu."""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401 (registruje tabuľky)
from .config import settings
from .routers import algorithms, experiments, generators, problems, visualize
from .seed import init_database


_ready = False
_lock = threading.Lock()


def ensure_ready() -> None:
    """Inicializácia databázy raz za proces. Serverless prostredie nemusí volať lifespan."""
    global _ready
    if _ready:
        return
    with _lock:
        if not _ready:
            init_database()
            _ready = True


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_ready()
    yield


app = FastAPI(title="AlgoLab API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def _init_db(request: Request, call_next):
    ensure_ready()
    return await call_next(request)


app.include_router(problems.router)
app.include_router(algorithms.router)
app.include_router(generators.router)
app.include_router(experiments.router)
app.include_router(visualize.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
