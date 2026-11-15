from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AnalysisModel, LoadCase, Material, Part, Project
from app.schemas import AnalysisCreate, LoadCaseCreate, MaterialCreate, PartCreate, ProjectCreate


def create_project(db: Session, payload: ProjectCreate) -> Project:
    project = Project(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        description=payload.description,
        status=payload.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_material(db: Session, payload: MaterialCreate) -> Material:
    material = Material(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        material_family=payload.material_family,
        density=payload.density,
        elastic_modulus=payload.elastic_modulus,
        poisson_ratio=payload.poisson_ratio,
        yield_strength=payload.yield_strength,
        source_type=payload.source_type,
        certified=payload.certified,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def create_part(db: Session, payload: PartCreate) -> Part:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    part = Part(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        part_code=payload.part_code,
        part_name=payload.part_name,
        part_type=payload.part_type,
        material_id=payload.material_id,
        thickness=payload.thickness,
        thickness_unit=payload.thickness_unit,
        status=payload.status,
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


def create_load_case(db: Session, payload: LoadCaseCreate) -> LoadCase:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    item = LoadCase(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        load_case_code=payload.load_case_code,
        name=payload.name,
        case_type=payload.case_type,
        description=payload.description,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_analysis(db: Session, payload: AnalysisCreate) -> AnalysisModel:
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
        analysis_type=payload.analysis_type,
        solver_type=payload.solver_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def build_workbench_summary(db: Session, project_id: str) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "project_name": db.query(Project).filter(Project.id == project_id).first().name,
        "materials_count": db.query(Material).count(),
        "parts_count": db.query(Part).filter(Part.project_id == project_id).count(),
        "load_cases_count": db.query(LoadCase).filter(LoadCase.project_id == project_id).count(),
        "analyses_count": db.query(AnalysisModel).filter(AnalysisModel.project_id == project_id).count(),
    }
