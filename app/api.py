from __future__ import annotations

import csv
import io
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import AnalysisModel, LoadCase, ManufacturingPackage, Material, Part, Project, ReviewRecord, WeldJoint
from app.services.workbench import (
    build_workbench_summary,
    create_analysis,
    create_load_case,
    create_manufacturing_package,
    create_material,
    create_part,
    create_project,
    create_review_record,
    create_weld_joint,
    read_seed_materials,
    seed_materials,
)

api_router = APIRouter(prefix="/api/v1")


class ProjectCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=120)
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    status: str = "draft"


class MaterialCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=120)
    name: str = Field(..., min_length=2, max_length=200)
    material_family: str = "HDPE"
    density: float | None = Field(default=None, gt=0)
    elastic_modulus: float | None = Field(default=None, gt=0)
    poisson_ratio: float | None = Field(default=None, gt=0, lt=0.5)
    yield_strength: float | None = Field(default=None, gt=0)
    source_type: str = "unverified"
    certified: bool = False
    notes: str | None = None


class PartCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    part_code: str = Field(..., min_length=1, max_length=120)
    part_name: str = Field(..., min_length=1, max_length=200)
    part_type: str = Field(..., min_length=1, max_length=80)
    material_id: str | None = None
    thickness: float | None = Field(default=None, gt=0)
    thickness_unit: str = "mm"
    status: str = "draft"
    notes: str | None = None


class LoadCaseCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    load_case_code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    case_type: str = "static"
    description: str | None = None


class AnalysisCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    load_case_id: str | None = None
    analysis_code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    analysis_type: str = "static"
    solver_type: str = "calculix"
    status: str = "draft"
    assumptions: str | None = None


class ManufacturePackageCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    package_type: str = "bom"
    status: str = "draft"
    notes: str | None = None


class WeldJointCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    joint_code: str = Field(..., min_length=1, max_length=120)
    weld_type: str = "butt"
    weld_process: str | None = None
    notes: str | None = None


class ReviewCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: str = Field(..., min_length=1)
    reviewer: str = Field(..., min_length=1, max_length=200)
    status: str = "in_review"
    comment: str | None = None


class WorkbenchSummary(BaseModel):
    project_id: str
    project_name: str
    materials_count: int
    parts_count: int
    load_cases_count: int
    analyses_count: int


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A record with the same unique code already exists") from exc


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict[str, int]:
    return {
        "projects_count": db.query(Project).count(),
        "materials_count": db.query(Material).count(),
        "parts_count": db.query(Part).count(),
        "load_cases_count": db.query(LoadCase).count(),
        "analyses_count": db.query(AnalysisModel).count(),
    }


@api_router.get("/meta")
def meta() -> dict[str, Any]:
    return {"app": "HDPE Ship Design Workbench", "version": "0.3.0", "seed_materials": read_seed_materials()}


@api_router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project_endpoint(project: ProjectCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        item = create_project(db, project)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Project code already exists") from exc
    return {"id": item.id, "code": item.code, "name": item.name, "status": item.status}


@api_router.get("/projects")
def list_projects(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [
        {"id": p.id, "code": p.code, "name": p.name, "description": p.description, "status": p.status}
        for p in db.query(Project).order_by(Project.created_at.desc()).all()
    ]


@api_router.get("/projects/{project_id}/summary")
def project_summary(project_id: str, db: Session = Depends(get_db)) -> WorkbenchSummary:
    payload = build_workbench_summary(db, project_id)
    return WorkbenchSummary(**payload)


@api_router.get("/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": project.id,
        "code": project.code,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "parts_count": db.query(Part).filter(Part.project_id == project_id).count(),
        "load_cases_count": db.query(LoadCase).filter(LoadCase.project_id == project_id).count(),
        "analyses_count": db.query(AnalysisModel).filter(AnalysisModel.project_id == project_id).count(),
    }


@api_router.get("/materials")
def list_materials(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "material_family": m.material_family,
            "density": m.density,
            "elastic_modulus": m.elastic_modulus,
            "poisson_ratio": m.poisson_ratio,
            "yield_strength": m.yield_strength,
            "source_type": m.source_type,
            "certified": m.certified,
            "notes": m.notes,
        }
        for m in db.query(Material).order_by(Material.code).all()
    ]


@api_router.post("/materials", status_code=status.HTTP_201_CREATED)
def create_material_endpoint(material: MaterialCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        item = create_material(db, material)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Material code already exists") from exc
    return {"id": item.id, "code": item.code, "name": item.name}


@api_router.post("/parts", status_code=status.HTTP_201_CREATED)
def create_part_endpoint(part: PartCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    project_exists = db.query(Project).filter(Project.id == part.project_id).first()
    if not project_exists:
        raise HTTPException(status_code=404, detail="Project not found")
    if part.material_id and not db.query(Material).filter(Material.id == part.material_id).first():
        raise HTTPException(status_code=404, detail="Material not found")
    try:
        item = create_part(db, part)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Part code already exists") from exc
    return {"id": item.id, "part_code": item.part_code, "part_name": item.part_name}


@api_router.get("/parts")
def list_parts(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(Part).options(joinedload(Part.material))
    if project_id:
        query = query.filter(Part.project_id == project_id)
    return [
        {
            "id": p.id,
            "project_id": p.project_id,
            "part_code": p.part_code,
            "part_name": p.part_name,
            "part_type": p.part_type,
            "material_id": p.material_id,
            "material_code": p.material.code if p.material else None,
            "thickness": p.thickness,
            "thickness_unit": p.thickness_unit,
            "status": p.status,
        }
        for p in query.order_by(Part.part_code).all()
    ]


@api_router.post("/load-cases", status_code=status.HTTP_201_CREATED)
def create_load_case_endpoint(payload: LoadCaseCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        item = create_load_case(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Load case code already exists") from exc
    return {"id": item.id, "code": item.load_case_code, "name": item.name}


@api_router.get("/load-cases")
def list_load_cases(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(LoadCase)
    if project_id:
        query = query.filter(LoadCase.project_id == project_id)
    return [
        {
            "id": c.id,
            "project_id": c.project_id,
            "code": c.load_case_code,
            "name": c.name,
            "case_type": c.case_type,
            "description": c.description,
        }
        for c in query.order_by(LoadCase.created_at.desc()).all()
    ]


@api_router.post("/analyses", status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.load_case_id and not db.query(LoadCase).filter(LoadCase.id == payload.load_case_id).first():
        raise HTTPException(status_code=404, detail="Load case not found")
    try:
        item = create_analysis(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Analysis code already exists") from exc
    return {"id": item.id, "code": item.analysis_code, "name": item.name, "status": item.status}


@api_router.get("/analyses")
def list_analyses(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(AnalysisModel)
    if project_id:
        query = query.filter(AnalysisModel.project_id == project_id)
    return [
        {
            "id": a.id,
            "project_id": a.project_id,
            "code": a.analysis_code,
            "name": a.name,
            "solver_type": a.solver_type,
            "analysis_type": a.analysis_type,
            "status": a.status,
        }
        for a in query.order_by(AnalysisModel.created_at.desc()).all()
    ]


@api_router.post("/manufacturing-packages", status_code=status.HTTP_201_CREATED)
def create_manufacturing_package_endpoint(payload: ManufacturePackageCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        item = create_manufacturing_package(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Manufacturing package name already exists") from exc
    return {"id": item.id, "name": item.name, "package_type": item.package_type, "status": item.status}


@api_router.get("/manufacturing-packages")
def list_manufacturing_packages(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(ManufacturingPackage)
    if project_id:
        query = query.filter(ManufacturingPackage.project_id == project_id)
    return [
        {
            "id": i.id,
            "project_id": i.project_id,
            "name": i.name,
            "package_type": i.package_type,
            "status": i.status,
            "notes": i.notes,
        }
        for i in query.order_by(ManufacturingPackage.created_at.desc()).all()
    ]


@api_router.post("/weld-joints", status_code=status.HTTP_201_CREATED)
def create_weld_joint_endpoint(payload: WeldJointCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        item = create_weld_joint(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Weld joint code already exists") from exc
    return {"id": item.id, "joint_code": item.joint_code, "weld_type": item.weld_type}


@api_router.get("/weld-joints")
def list_weld_joints(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(WeldJoint)
    if project_id:
        query = query.filter(WeldJoint.project_id == project_id)
    return [
        {
            "id": w.id,
            "project_id": w.project_id,
            "joint_code": w.joint_code,
            "weld_type": w.weld_type,
            "weld_process": w.weld_process,
            "notes": w.notes,
        }
        for w in query.order_by(WeldJoint.joint_code).all()
    ]


@api_router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review_endpoint(payload: ReviewCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    item = create_review_record(db, payload)
    return {"id": item.id, "status": item.status, "reviewer": item.reviewer}


@api_router.get("/reviews")
def list_reviews(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = db.query(ReviewRecord)
    if project_id:
        query = query.filter(ReviewRecord.project_id == project_id)
    return [
        {
            "id": r.id,
            "project_id": r.project_id,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "reviewer": r.reviewer,
            "status": r.status,
            "comment": r.comment,
        }
        for r in query.order_by(ReviewRecord.created_at.desc()).all()
    ]


def _csv_safe(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


@api_router.get("/projects/{project_id}/manufacturing/bom.csv")
def export_bom(project_id: str, db: Session = Depends(get_db)) -> Response:
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    parts = db.query(Part).options(joinedload(Part.material)).filter(Part.project_id == project_id).order_by(Part.part_code).all()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Part code", "Name", "Type", "Material", "Thickness", "Thickness unit", "Status"])
    for part in parts:
        writer.writerow([
            _csv_safe(part.part_code),
            _csv_safe(part.part_name),
            _csv_safe(part.part_type),
            _csv_safe(part.material.code if part.material else ""),
            part.thickness or "",
            _csv_safe(part.thickness_unit),
            _csv_safe(part.status),
        ])
    return Response(
        content="\ufeff" + output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="bom-{project_id}.csv"'},
    )
