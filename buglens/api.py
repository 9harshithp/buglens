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
    from .modules import DefectAnalyzer, DefectReport, DefectScorer, DefectValidator
except ImportError:
    from modules import DefectAnalyzer, DefectReport, DefectScorer, DefectValidator

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


@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "buglens", "version": "1.0.0"}


@app.post("/analyze", response_model=AnalyzeResponse, tags=["defects"])
def analyze(payload: DefectPayload) -> Dict:
    """Full pipeline: validate → score → rewrite. Returns a single JSON payload."""
    return _analyzer.analyze(payload.model_dump()).to_dict()


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
