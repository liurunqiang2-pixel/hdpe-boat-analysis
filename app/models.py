from __future__ import annotations

from sqlalchemy import String, Float, ForeignKey, Integer, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parts: Mapped[list["Part"]] = relationship(back_populates="project")
    load_cases: Mapped[list["LoadCase"]] = relationship(back_populates="project")
    analyses: Mapped[list["AnalysisModel"]] = relationship(back_populates="project")


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    material_family: Mapped[str] = mapped_column(String(100), default="HDPE")
    density: Mapped[float | None] = mapped_column(Float, nullable=True)
    elastic_modulus: Mapped[float | None] = mapped_column(Float, nullable=True)
    poisson_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    yield_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="certified")
    certified: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parts: Mapped[list["Part"]] = relationship(back_populates="material")


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    part_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    part_name: Mapped[str] = mapped_column(String(200), nullable=False)
    part_type: Mapped[str] = mapped_column(String(80), nullable=False)
    material_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("materials.id"), nullable=True)
    thickness: Mapped[float | None] = mapped_column(Float, nullable=True)
    thickness_unit: Mapped[str] = mapped_column(String(20), default="mm")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="parts")
    material: Mapped[Material | None] = relationship(back_populates="parts")


class LoadCase(Base):
    __tablename__ = "load_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    load_case_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    case_type: Mapped[str] = mapped_column(String(80), default="static")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="load_cases")
    analyses: Mapped[list["AnalysisModel"]] = relationship(back_populates="load_case")


class AnalysisModel(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    load_case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("load_cases.id"), nullable=True)
    analysis_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(100), default="static")
    solver_type: Mapped[str] = mapped_column(String(80), default="calculix")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    assumptions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="analyses")
    load_case: Mapped[LoadCase | None] = relationship(back_populates="analyses")


class WeldJoint(Base):
    __tablename__ = "weld_joints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    joint_code: Mapped[str] = mapped_column(String(120), unique=True)
    weld_type: Mapped[str] = mapped_column(String(100), default="fillet")
    weld_process: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ManufacturingPackage(Base):
    __tablename__ = "manufacturing_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    package_type: Mapped[str] = mapped_column(String(80), default="bom")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReviewRecord(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="in_review")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
