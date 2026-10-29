"""FastAPI aplikácia — vstupný bod backendu (tenký vertikálny rez)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401 — registruje tabuľky na Base
from .config import settings
from .db import Base, SessionLocal, engine
from .routers import algorithms, experiments, generators, problems, visualize
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title="ALGO_ANALYZER API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems.router)
app.include_router(algorithms.router)
app.include_router(generators.router)
app.include_router(experiments.router)
app.include_router(visualize.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
