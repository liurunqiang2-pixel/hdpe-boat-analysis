from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import AnalysisModel, LoadCase, Material, Part, Project


def read_seed_materials() -> list[dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "hdpe_materials.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def seed_materials(db: Session) -> None:
    if db.query(Material).count() > 0:
        return
    for entry in read_seed_materials():
        db.add(Material(**entry))
    db.commit()


def build_workbench_summary(db: Session, project_id: str) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    return {
        "project_id": project_id,
        "project_name": project.name if project else "",
        "materials_count": db.query(Material).count(),
        "parts_count": db.query(Part).filter(Part.project_id == project_id).count(),
        "load_cases_count": db.query(LoadCase).filter(LoadCase.project_id == project_id).count(),
        "analyses_count": db.query(AnalysisModel).filter(AnalysisModel.project_id == project_id).count(),
    }
