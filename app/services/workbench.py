from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AnalysisModel, LoadCase, Material, Part, Project


def create_project(db: Session, payload: Any) -> Project:
    project = Project(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        description=getattr(payload, "description", None),
        status=getattr(payload, "status", "draft"),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_material(db: Session, payload: Any) -> Material:
    material = Material(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        material_family=getattr(payload, "material_family", "HDPE"),
        density=getattr(payload, "density", None),
        elastic_modulus=getattr(payload, "elastic_modulus", None),
        poisson_ratio=getattr(payload, "poisson_ratio", None),
        yield_strength=getattr(payload, "yield_strength", None),
        source_type=getattr(payload, "source_type", "certified"),
        certified=getattr(payload, "certified", False),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def create_part(db: Session, payload: Any) -> Part:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    part = Part(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        part_code=payload.part_code,
        part_name=payload.part_name,
        part_type=payload.part_type,
        material_id=getattr(payload, "material_id", None),
        thickness=getattr(payload, "thickness", None),
        thickness_unit=getattr(payload, "thickness_unit", "mm"),
        status=getattr(payload, "status", "draft"),
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


def create_load_case(db: Session, payload: Any) -> LoadCase:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    item = LoadCase(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        load_case_code=payload.load_case_code,
        name=payload.name,
        case_type=getattr(payload, "case_type", "static"),
        description=getattr(payload, "description", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_analysis(db: Session, payload: Any) -> AnalysisModel:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.load_case_id and not db.query(LoadCase).filter(LoadCase.id == payload.load_case_id).first():
        raise HTTPException(status_code=404, detail="Load case not found")
    item = AnalysisModel(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        load_case_id=payload.load_case_id,
        analysis_code=payload.analysis_code,
        name=payload.name,
        analysis_type=getattr(payload, "analysis_type", "static"),
        solver_type=getattr(payload, "solver_type", "calculix"),
        status="draft",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def read_seed_materials() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[1] / "data" / "hdpe_materials.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def seed_materials(db: Session) -> None:
    if db.query(Material).count() > 0:
        return
    for entry in read_seed_materials():
        db.add(Material(**entry))
    db.commit()


def build_workbench_summary(db: Session, project_id: str) -> dict[str, Any]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project_id": project_id,
        "project_name": project.name,
        "materials_count": db.query(Material).count(),
        "parts_count": db.query(Part).filter(Part.project_id == project_id).count(),
        "load_cases_count": db.query(LoadCase).filter(LoadCase.project_id == project_id).count(),
        "analyses_count": db.query(AnalysisModel).filter(AnalysisModel.project_id == project_id).count(),
    }
