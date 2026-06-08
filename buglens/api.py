"""
BugLens REST API — minimal FastAPI surface for the analyzer.

Three endpoints:
  GET  /health          — liveness probe
  POST /analyze         — full analyze pipeline (validate + score + rewrite)
  POST /validate        — validation issues only (no rewrite, no score)
  POST /score           — quality score only

Run with:  uvicorn api:app --reload --port 8001
The OpenAPI spec is auto-generated and importable into Postman.
"""
from __future__ import annotations

from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .modules import BugLensStore, DefectAnalyzer, DefectReport, DefectScorer, DefectValidator
except ImportError:
    from modules import BugLensStore, DefectAnalyzer, DefectReport, DefectScorer, DefectValidator

app = FastAPI(
    title="BugLens — Defect Quality Checker API",
    version="1.0.0",
    description="REST API for analyzing software defect report quality.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class DefectPayload(BaseModel):
    title: str = ""
    description: str = ""
    steps_to_reproduce: str = ""
    expected_result: str = ""
    actual_result: str = ""
    environment: str = ""
    severity: str = ""


class AnalyzeResponse(BaseModel):
    report: Dict
    issues: list
    score: Dict
    rewrite: Dict


# Singleton analyzer — FastAPI reuses it across requests.
_analyzer = DefectAnalyzer()
_store = BugLensStore()


@app.get("/", tags=["meta"])
def root() -> Dict[str, object]:
    return {
        "status": "ok",
        "service": "buglens",
        "version": "1.0.0",
        "available_endpoints": [
            "/health",
            "/analyze",
            "/validate",
            "/score",
            "/history",
            "/docs",
        ],
    }


@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "buglens", "version": "1.0.0"}


@app.post("/analyze", response_model=AnalyzeResponse, tags=["defects"])
def analyze(payload: DefectPayload) -> Dict:
    """Full pipeline: validate → score → rewrite. Returns a single JSON payload."""
    analysis = _analyzer.analyze(payload.model_dump())
    _store.save_analysis(payload.model_dump(), analysis)
    return analysis.to_dict()


@app.post("/validate", tags=["defects"])
def validate(payload: DefectPayload) -> Dict:
    """Return just the validation issues (no score, no rewrite)."""
    report = DefectReport.from_dict(payload.model_dump())
    issues = DefectValidator().validate(report)
    return {"issues": [i.to_dict() for i in issues]}


@app.post("/score", tags=["defects"])
def score(payload: DefectPayload) -> Dict:
    """Return just the quality score and section breakdown."""
    report = DefectReport.from_dict(payload.model_dump())
    issues = DefectValidator().validate(report)
    return DefectScorer().score(report, issues).to_dict()


@app.get("/history", tags=["history"])
def history(limit: int = 24) -> Dict[str, object]:
    items = [_store.to_json_record(record) for record in _store.list_analyses(limit=limit)]
    return {"items": items, "count": len(items)}


@app.get("/history/{analysis_id}", tags=["history"])
def get_history_item(analysis_id: str) -> Dict[str, object]:
    record = _store.get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _store.to_json_record(record)


@app.delete("/history", tags=["history"])
def clear_history() -> Dict[str, object]:
    deleted = _store.clear_analyses()
    return {"status": "ok", "deleted": deleted}


@app.delete("/history/{analysis_id}", tags=["history"])
def delete_history_item(analysis_id: str) -> Dict[str, object]:
    deleted = _store.delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "ok", "deleted": True}
