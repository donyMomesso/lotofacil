from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from audit_core import BRAIN_VERSION, build_report
from checkpoint import load_draws

DATA_PATH = Path(os.getenv("LOTOFACIL_HISTORICO", "historico.json"))
app = FastAPI(title="Cérebro Python — Auditoria Histórica", version=BRAIN_VERSION)


class ContestInput(BaseModel):
    concurso: int = Field(gt=0)
    dezenas: list[int] = Field(min_length=15, max_length=15)
    data: str | None = None


class AuditInput(BaseModel):
    concursos: list[ContestInput] = Field(min_length=31)
    min_training: int = Field(default=30, ge=8, le=500)


def report_from_file() -> dict:
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Histórico ainda não foi disponibilizado ao cérebro Python.")
    try:
        return build_report(load_draws(DATA_PATH))
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/saude")
def health() -> dict:
    return {
        "status": "ok",
        "brain_version": BRAIN_VERSION,
        "purpose": "historical_education_only",
        "source_of_truth": "python",
    }


@app.get("/auditoria-historica")
def historical_audit() -> dict:
    return report_from_file()


@app.get("/checkpoint-5")
def checkpoint_five() -> dict:
    report = report_from_file()
    return {
        "ok": report["ok"],
        "purpose": report["purpose"],
        "brain_version": report["brain_version"],
        "latest_checkpoint": report["latest_checkpoint"],
        "completed_checkpoint_contests": report["completed_checkpoint_contests"],
        "pending_until_next_checkpoint": report["pending_until_next_checkpoint"],
        "integrity": report["integrity"],
        "report_hash": report["report_hash"],
    }


@app.post("/auditoria-historica")
def historical_audit_payload(payload: AuditInput) -> dict:
    values = [item.model_dump() for item in payload.concursos]
    try:
        return build_report(values, min_training=payload.min_training)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
