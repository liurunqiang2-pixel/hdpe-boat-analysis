# HDPE Ship Design Workbench

A lightweight engineering prototype for managing HDPE vessel design projects, materials, parts, load cases, analyses, weld joints, review records, and manufacturing packages.

## Features

- Project dashboard with summary counts
- Material catalog with engineering metadata
- Parts linked to project and material records
- Load case and structural analysis tracking
- Weld joint management
- Manufacturing package tracking
- BOM CSV export for project parts
- Seeded sample material data for local prototype use

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/ for the dashboard
- http://127.0.0.1:8000/docs for the interactive API docs

## API highlights

- GET /api/v1/dashboard
- GET|POST /api/v1/projects
- GET|POST /api/v1/materials
- GET|POST /api/v1/parts
- GET|POST /api/v1/load-cases
- GET|POST /api/v1/analyses
- GET|POST /api/v1/weld-joints
- GET|POST /api/v1/manufacturing-packages
- GET|POST /api/v1/reviews
- GET /api/v1/projects/{project_id}/manufacturing/bom.csv
- GET /api/v1/projects/{project_id}/summary

## Engineering note

The material values and calculations are sample prototype data only and should never be treated as approved design allowables. All design and manufacturing decisions require verification against certified supplier data, applicable rules, and qualified engineering review.
