"""
main.py — Minimal FastAPI website for demoing Member B's Simulation & Rules
Engine live.

This is a thin demo wrapper, not the full Chronos product API (that's
Member A/C's job — see routes_decision.py etc. in the Technical Brief).
It exists so this repo can be run as an actual website for a team demo or
submission video, with zero other dependencies.

Run it with:
    uvicorn main:app --reload

Then open:
    http://127.0.0.1:8000/            -> the visual demo dashboard
    http://127.0.0.1:8000/docs        -> interactive Swagger API docs
    http://127.0.0.1:8000/api/samples -> list of seeded sample decisions
    POST /api/simulate                -> run the engine on a custom DecisionInput
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.engine import DecisionInput, SimulationEngine, SimulationResult
from app.engine.sample_data import ALL_SAMPLES

BASE_DIR = Path(__file__).resolve().parent
DEMO_DIR = BASE_DIR / "demo"

app = FastAPI(
    title="Project Chronos — Simulation & Rules Engine",
    description=(
        "Member B's deterministic decision engine: Rule Engine, Scenario "
        "Generator, Confidence Calculator, and Forecasting Logic. "
        "No ML, no LLM — every number is a plain Python formula."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SimulationEngine()


@app.get("/", include_in_schema=False)
def serve_dashboard() -> FileResponse:
    """Serves the static visual demo dashboard at the site root."""
    index_path = DEMO_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="demo/index.html not found")
    return FileResponse(index_path)


@app.get("/api/samples", tags=["demo"])
def list_samples() -> list[str]:
    """Returns the names of the seeded sample decisions available to run."""
    return list(ALL_SAMPLES.keys())


@app.get("/api/samples/{name}", response_model=SimulationResult, tags=["demo"])
def run_sample(name: str) -> SimulationResult:
    """Runs the engine on one of the seeded sample decisions and returns the result."""
    if name not in ALL_SAMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown sample '{name}'. Available: {list(ALL_SAMPLES.keys())}",
        )
    decision = ALL_SAMPLES[name]()
    return engine.run(decision)


@app.get("/api/samples/{name}/input", tags=["demo"])
def get_sample_input(name: str) -> JSONResponse:
    """Returns the raw DecisionInput used for a given sample, for reference."""
    if name not in ALL_SAMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown sample '{name}'. Available: {list(ALL_SAMPLES.keys())}",
        )
    decision = ALL_SAMPLES[name]()
    return JSONResponse(content=decision.model_dump(mode="json"))


@app.post("/api/simulate", response_model=SimulationResult, tags=["engine"])
def simulate(decision: DecisionInput) -> SimulationResult:
    """
    Core endpoint — mirrors the /decisions/simulate contract from the
    Technical Brief (Section 8.1). Accepts a full DecisionInput and returns
    three computed scenarios plus a confidence score. No LLM is called here.
    """
    return engine.run(decision)


@app.get("/api/health", tags=["engine"])
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "chronos-rule-engine-v1"}


# Serve any other static assets placed in demo/ (images, css, etc.) if added later.
if DEMO_DIR.exists():
    app.mount("/demo", StaticFiles(directory=str(DEMO_DIR)), name="demo")
