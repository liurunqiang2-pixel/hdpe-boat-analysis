from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    status: str = "draft"


class ProjectOut(BaseModel):
    id: str
    code: str
    name: str
    description: str | None = None
    status: str


class MaterialCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    material_family: str = "HDPE"
    density: float | None = Field(default=None, gt=0)
    elastic_modulus: float | None = Field(default=None, gt=0)
    poisson_ratio: float | None = Field(default=None, gt=0, lt=0.5)
    yield_strength: float | None = Field(default=None, gt=0)
    source_type: str = "unverified"
    certified: bool = False
    notes: str | None = None


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
    part_code: str = Field(..., min_length=1, max_length=120)
    part_name: str = Field(..., min_length=1, max_length=200)
    part_type: str = Field(..., min_length=1, max_length=80)
    material_id: str | None = None
    thickness: float | None = Field(default=None, gt=0)
    thickness_unit: str = "mm"
    status: str = "draft"


class LoadCaseCreate(BaseModel):
    project_id: str
    load_case_code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    case_type: str = "static"
    description: str | None = None


class AnalysisCreate(BaseModel):
    project_id: str
    load_case_id: str | None = None
    analysis_code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=200)
    analysis_type: str = "static"
    solver_type: str = "calculix"


class ManufacturingPackageCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=200)
    package_type: str = "bom"
    notes: str | None = None


class WeldJointCreate(BaseModel):
    project_id: str
    joint_code: str = Field(..., min_length=1, max_length=120)
    weld_type: str = "butt"
    weld_process: str | None = None
    notes: str | None = None


class WorkbenchSummary(BaseModel):
    project_id: str
    project_name: str
    materials_count: int
    parts_count: int
    load_cases_count: int
    analyses_count: int
