# HDPE Ship Design Workbench

This repository includes a lightweight prototype for managing HDPE vessel design project data. It provides a dashboard and API for projects, materials, parts, load cases, analyses, welding records, and manufacturing packages.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/> for the dashboard and <http://127.0.0.1:8000/docs> for interactive API documentation. The app creates its SQLite database under `data/` and seeds the sample material catalog on startup.

## API overview

- `GET /api/v1/dashboard` — summary counts
- `GET|POST /api/v1/projects`
- `GET|POST /api/v1/materials`
- `GET|POST /api/v1/parts` (`project_id` query parameter filters parts)
- `GET|POST /api/v1/load-cases`
- `GET|POST /api/v1/analyses`
- `GET|POST /api/v1/weld-joints`
- `GET|POST /api/v1/manufacturing-packages`
- `GET /api/v1/projects/{project_id}/manufacturing/bom.csv` — BOM export
- `GET /api/v1/projects/{project_id}/summary`

## Engineering limitations

The sample HDPE values are placeholders for application development, not approved design allowables. The app does not perform vessel design approval or FEA calculations. Verify material properties, welding procedures, load cases, rules, and results with traceable data and qualified naval architects/engineers before using them in real design or construction.
