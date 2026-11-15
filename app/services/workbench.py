from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import AnalysisModel, LoadCase, Material, Part, Project, ReviewRecord, ManufacturingPackage, WeldJoint


SEED_MATERIALS = [
    {
        "code": "HDPE-PE100",
        "name": "Marine PE100 HDPE",
        "material_family": "HDPE",
        "density": 0.96,
        "elastic_modulus": 900.0,
        "poisson_ratio": 0.42,
        "yield_strength": 22.0,
        "source_type": "sample",
        "certified": False,
        "notes": "Reference sample only; not a certified design allowable.",
    },
    {
        "code": "HDPE-PE80",
        "name": "Marine PE80 HDPE",
        "material_family": "HDPE",
        "density": 0.95,
        "elastic_modulus": 850.0,
        "poisson_ratio": 0.41,
        "yield_strength": 20.0,
        "source_type": "sample",
        "certified": False,
        "notes": "Reference sample only; verify against supplier data sheets.",
    },
    {
        "code": "HDPE-PE100-CF",
        "name": "Reinforced PE100 Composite HDPE",
        "material_family": "HDPE",
        "density": 1.02,
        "elastic_modulus": 1200.0,
        "poisson_ratio": 0.40,
        "yield_strength": 26.0,
        "source_type": "sample",
        "certified": False,
        "notes": "Sample composite formulation for concept evaluation.",
    },
]


def create_project(db: Session, payload: Any) -> Project:
    item = Project(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        description=getattr(payload, "description", None),
        status=getattr(payload, "status", "draft"),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_material(db: Session, payload: Any) -> Material:
    item = Material(
        id=str(uuid.uuid4()),
        code=payload.code,
        name=payload.name,
        material_family=getattr(payload, "material_family", "HDPE"),
        density=getattr(payload, "density", None),
        elastic_modulus=getattr(payload, "elastic_modulus", None),
        poisson_ratio=getattr(payload, "poisson_ratio", None),
        yield_strength=getattr(payload, "yield_strength", None),
        source_type=getattr(payload, "source_type", "unverified"),
        certified=getattr(payload, "certified", False),
        notes=getattr(payload, "notes", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_part(db: Session, payload: Any) -> Part:
    item = Part(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        part_code=payload.part_code,
        part_name=payload.part_name,
        part_type=payload.part_type,
        material_id=payload.material_id,
        thickness=getattr(payload, "thickness", None),
        thickness_unit=getattr(payload, "thickness_unit", "mm"),
        status=getattr(payload, "status", "draft"),
        notes=getattr(payload, "notes", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_load_case(db: Session, payload: Any) -> LoadCase:
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
    item = AnalysisModel(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        load_case_id=getattr(payload, "load_case_id", None),
        analysis_code=payload.analysis_code,
        name=payload.name,
        analysis_type=getattr(payload, "analysis_type", "static"),
        solver_type=getattr(payload, "solver_type", "calculix"),
        status=getattr(payload, "status", "draft"),
        assumptions=getattr(payload, "assumptions", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def build_workbench_summary(db: Session, project_id: str) -> dict[str, Any]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise ValueError("Project not found")
    return {
        "project_id": project.id,
        "project_name": project.name,
        "materials_count": db.query(Material).count(),
        "parts_count": db.query(Part).filter(Part.project_id == project_id).count(),
        "load_cases_count": db.query(LoadCase).filter(LoadCase.project_id == project_id).count(),
        "analyses_count": db.query(AnalysisModel).filter(AnalysisModel.project_id == project_id).count(),
    }


def read_seed_materials() -> list[dict[str, Any]]:
    return SEED_MATERIALS


def seed_materials(db: Session) -> None:
    existing = db.query(Material).count()
    if existing:
        return
    for row in SEED_MATERIALS:
        material = Material(
            id=str(uuid.uuid4()),
            code=row["code"],
            name=row["name"],
            material_family=row["material_family"],
            density=row["density"],
            elastic_modulus=row["elastic_modulus"],
            poisson_ratio=row["poisson_ratio"],
            yield_strength=row["yield_strength"],
            source_type=row["source_type"],
            certified=row["certified"],
            notes=row["notes"],
        )
        db.add(material)
    db.commit()


def create_review_record(db: Session, payload: Any) -> ReviewRecord:
    item = ReviewRecord(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        reviewer=payload.reviewer,
        status=getattr(payload, "status", "in_review"),
        comment=getattr(payload, "comment", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_weld_joint(db: Session, payload: Any) -> WeldJoint:
    item = WeldJoint(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        joint_code=payload.joint_code,
        weld_type=getattr(payload, "weld_type", "butt"),
        weld_process=getattr(payload, "weld_process", None),
        notes=getattr(payload, "notes", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_manufacturing_package(db: Session, payload: Any) -> ManufacturingPackage:
    item = ManufacturingPackage(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        name=payload.name,
        package_type=getattr(payload, "package_type", "bom"),
        status=getattr(payload, "status", "draft"),
        notes=getattr(payload, "notes", None),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
