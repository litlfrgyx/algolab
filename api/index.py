"""Vstupný bod hlavného Vercel projektu: FastAPI aplikácia z priečinka backend.

Vercel spustí túto funkciu pre každú požiadavku na /api/*. Kód používateľa sa
tu nespúšťa, posiela sa na samostatný runner (RUNNER_URL), ktorý nemá prístup
k databáze.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "runner"))

from app.main import app  # noqa: E402,F401
