from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    description: str | None = None
    status: str = "draft"


class ProjectOut(BaseModel):
    id: str
    code: str
    name: str
    description: str | None = None
    status: str


class MaterialCreate(BaseModel):
    code: str
    name: str
    material_family: str = "HDPE"
    density: float | None = None
    elastic_modulus: float | None = None
    poisson_ratio: float | None = None
    yield_strength: float | None = None
    source_type: str = "certified"
    certified: bool = False


class MaterialOut(BaseModel):
    id: str
    code: str
    name: str
    material_family: str
    density: float | None = None
    elastic_modulus: float | None = None
    poisson_ratio: float | None = None
    yield_strength: float | None = None
    source_type: str
    certified: bool


class PartCreate(BaseModel):
    project_id: str
    part_code: str
    part_name: str
    part_type: str
    material_id: str | None = None
    thickness: float | None = None
    thickness_unit: str = "mm"
    status: str = "draft"


class LoadCaseCreate(BaseModel):
    project_id: str
    load_case_code: str
    name: str
    case_type: str = "static"
    description: str | None = None


class AnalysisCreate(BaseModel):
    project_id: str
    load_case_id: str | None = None
    analysis_code: str
    name: str
    analysis_type: str = "static"
    solver_type: str = "calculix"


class WorkbenchSummary(BaseModel):
    project_id: str
    project_name: str
    materials_count: int
    parts_count: int
    load_cases_count: int
    analyses_count: int
