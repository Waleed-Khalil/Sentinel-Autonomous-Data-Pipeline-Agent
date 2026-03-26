# Sentinel — Autonomous Data Pipeline Monitoring Agent

A self-healing data pipeline monitoring system powered by Claude. Sentinel continuously monitors simulated Airflow DAGs, detects anomalies (schema drift, null spikes, statistical outliers), and autonomously resolves 85%+ of failures using Claude's reasoning.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│   React UI  │◄──►│  FastAPI API  │◄──►│   PostgreSQL   │
│  Dashboard  │    │  + SSE Stream │    │  (DAGs, Runs,  │
│  (Tailwind) │    │              │    │   Anomalies)   │
└─────────────┘    └──────┬───────┘    └────────────────┘
                          │
                   ┌──────▼───────┐
                   │  Claude API  │
                   │  (Analysis & │
                   │  Remediation)│
                   └──────────────┘
```

**Anomaly Types Detected:**
- **Schema Drift** — columns added, removed, or type changed
- **Null Spikes** — null percentage exceeds configurable threshold
- **Statistical Anomalies** — values outside expected range (3σ)

**Self-Healing Actions:**
- Skip bad records
- Apply default values
- Trigger DAG retry
- Quarantine anomalous records

## Quick Start

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 2. Start all services

```bash
docker-compose up --build
```

### 3. Seed the database

```bash
docker-compose exec api python seed.py
```

### 4. Open the dashboard

Visit **http://localhost:5173**

## Walkthrough: Triggering and Watching Self-Healing

1. **Seed the database** — `docker-compose exec api python seed.py` populates 12 DAGs with realistic data and injected failures (null spikes, schema drift, statistical anomalies).

2. **Open the dashboard** — You'll see the Pipeline Health grid. DAGs with injected failures show as "warning" or "critical" status.

3. **Trigger a scan** — Click any DAG card, then click **"Trigger Scan"**. The agent will:
   - Detect anomalies in the latest run data
   - Send anomaly context to Claude for analysis
   - Claude recommends and applies a remediation action
   - Results appear immediately in the Anomaly panel

4. **Watch live alerts** — The sidebar shows real-time SSE alerts as anomalies are detected and resolved.

5. **Review the audit log** — Navigate to "Audit Log" to see every autonomous decision with Claude's reasoning.

6. **Background scanning** — The agent also runs a continuous background scan every 60 seconds, automatically detecting and resolving new anomalies.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stats` | Dashboard statistics |
| GET | `/api/v1/pipelines` | List all DAGs with health status |
| GET | `/api/v1/pipelines/{dag_id}` | DAG detail with runs, anomalies, data |
| POST | `/api/v1/pipelines/{dag_id}/scan` | Trigger anomaly scan |
| GET | `/api/v1/alerts` | All detected anomalies |
| GET | `/api/v1/alerts/{alert_id}` | Single alert detail |
| GET | `/api/v1/audit` | Full audit log |
| GET | `/api/v1/stream` | SSE live alert stream |

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy (async), Claude API
- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
- **Database:** PostgreSQL 16
- **Infrastructure:** Docker Compose

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # All API endpoints
│   │   ├── core/config.py         # Settings
│   │   ├── core/database.py       # Async SQLAlchemy setup
│   │   ├── models/models.py       # ORM models
│   │   ├── schemas/schemas.py     # Pydantic response schemas
│   │   ├── services/
│   │   │   ├── anomaly_detector.py # 3-type anomaly detection
│   │   │   ├── claude_healer.py    # Claude-powered remediation
│   │   │   ├── scanner.py          # Background scanning loop
│   │   │   └── sse_manager.py      # SSE event broadcasting
│   │   └── main.py                # FastAPI app
│   ├── init.sql                   # Database schema
│   ├── seed.py                    # Data seeding with failures
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/            # UI components
│   │   ├── hooks/                 # useApi, useSSE
│   │   ├── pages/                 # Dashboard, PipelineDetail, Alerts, Audit
│   │   ├── types/                 # TypeScript interfaces
│   │   └── App.tsx
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```
