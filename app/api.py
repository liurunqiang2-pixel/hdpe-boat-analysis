from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AnalysisModel, LoadCase, ManufacturingPackage, Material, Part, Project
from app.schemas import AnalysisCreate, LoadCaseCreate, MaterialCreate, PartCreate, ProjectCreate, WorkbenchSummary
from app.services.workbench import (
    build_workbench_summary,
    create_analysis,
    create_load_case,
    create_material,
    create_part,
    create_project,
)

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project_endpoint(project: ProjectCreate, db: Session = Depends(get_db)) -> dict:
    item = create_project(db, project)
    return {"id": item.id, "code": item.code, "name": item.name, "status": item.status}


@api_router.get("/projects")
def list_projects(db: Session = Depends(get_db)) -> list[dict]:
    return [{"id": p.id, "code": p.code, "name": p.name, "status": p.status} for p in db.query(Project).all()]


@api_router.get("/projects/{project_id}/summary")
def project_summary(project_id: str, db: Session = Depends(get_db)) -> WorkbenchSummary:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    summary = build_workbench_summary(db, project_id)
    return WorkbenchSummary(**summary)


@api_router.get("/materials")
def list_materials(db: Session = Depends(get_db)) -> list[dict]:
    return [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "material_family": m.material_family,
            "certified": m.certified,
            "elastic_modulus": m.elastic_modulus,
        }
        for m in db.query(Material).all()
    ]


@api_router.post("/materials", status_code=status.HTTP_201_CREATED)
def create_material_endpoint(material: MaterialCreate, db: Session = Depends(get_db)) -> dict:
    item = create_material(db, material)
    return {"id": item.id, "code": item.code, "name": item.name}


@api_router.post("/parts", status_code=status.HTTP_201_CREATED)
def create_part_endpoint(part: PartCreate, db: Session = Depends(get_db)) -> dict:
    item = create_part(db, part)
    return {"id": item.id, "part_code": item.part_code, "part_name": item.part_name}


@api_router.post("/load-cases", status_code=status.HTTP_201_CREATED)
def create_load_case_endpoint(payload: LoadCaseCreate, db: Session = Depends(get_db)) -> dict:
    item = create_load_case(db, payload)
    return {"id": item.id, "code": item.load_case_code, "name": item.name}


@api_router.post("/analyses", status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)) -> dict:
    item = create_analysis(db, payload)
    return {"id": item.id, "code": item.analysis_code, "name": item.name}


@api_router.get("/analyses")
def list_analyses(db: Session = Depends(get_db)) -> list[dict]:
    items = db.query(AnalysisModel).all()
    return [
        {"id": a.id, "code": a.analysis_code, "name": a.name, "solver_type": a.solver_type, "status": a.status}
        for a in items
    ]


@api_router.get("/manufacturing-packages")
def list_manufacturing_packages(db: Session = Depends(get_db)) -> list[dict]:
    items = db.query(ManufacturingPackage).all()
    return [{"id": i.id, "name": i.name, "package_type": i.package_type, "status": i.status} for i in items]
