from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db
from app.models.models import Anomaly, AuditLog, Dag, DagRun, PipelineData
from app.schemas.schemas import (
    AnomalyResponse,
    AuditLogResponse,
    DagDetailResponse,
    DagResponse,
    DagRunResponse,
    ScanResponse,
    StatsResponse,
)
from app.services.anomaly_detector import AnomalyDetector
from app.services.claude_healer import ClaudeHealer
from app.services.sse_manager import sse_manager

router = APIRouter(prefix="/api/v1")

detector = AnomalyDetector()
healer = ClaudeHealer()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_dags = (await db.execute(select(func.count()).select_from(Dag))).scalar()
    active_alerts = (await db.execute(
        select(func.count()).where(Anomaly.status == "detected")
    )).scalar()
    total_anomalies = (await db.execute(select(func.count()).select_from(Anomaly))).scalar()
    resolved_anomalies = (await db.execute(
        select(func.count()).where(Anomaly.status == "resolved")
    )).scalar()
    resolution_rate = resolved_anomalies / total_anomalies if total_anomalies > 0 else 0.0

    return StatsResponse(
        total_dags=total_dags,
        active_alerts=active_alerts,
        total_anomalies=total_anomalies,
        resolved_anomalies=resolved_anomalies,
        resolution_rate=round(resolution_rate, 4),
    )


@router.get("/pipelines", response_model=list[DagResponse])
async def list_pipelines(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dag).order_by(Dag.dag_id))
    dags = result.scalars().all()

    responses = []
    for dag in dags:
        # Get anomaly count
        anomaly_count = (await db.execute(
            select(func.count()).where(
                Anomaly.dag_id == dag.dag_id,
                Anomaly.status == "detected",
            )
        )).scalar()

        # Get last run time
        last_run = (await db.execute(
            select(DagRun.started_at)
            .where(DagRun.dag_id == dag.dag_id)
            .order_by(DagRun.started_at.desc())
            .limit(1)
        )).scalar_one_or_none()

        responses.append(DagResponse(
            id=dag.id,
            dag_id=dag.dag_id,
            name=dag.name,
            description=dag.description,
            schedule=dag.schedule,
            source_type=dag.source_type,
            status=dag.status,
            created_at=dag.created_at,
            updated_at=dag.updated_at,
            anomaly_count=anomaly_count,
            last_run_time=last_run,
        ))

    return responses


@router.get("/pipelines/{dag_id}", response_model=DagDetailResponse)
async def get_pipeline(dag_id: str, db: AsyncSession = Depends(get_db)):
    dag_result = await db.execute(select(Dag).where(Dag.dag_id == dag_id))
    dag = dag_result.scalar_one_or_none()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")

    # Get anomaly count and last run
    anomaly_count = (await db.execute(
        select(func.count()).where(Anomaly.dag_id == dag_id, Anomaly.status == "detected")
    )).scalar()
    last_run_time = (await db.execute(
        select(DagRun.started_at).where(DagRun.dag_id == dag_id)
        .order_by(DagRun.started_at.desc()).limit(1)
    )).scalar_one_or_none()

    # Recent runs
    runs_result = await db.execute(
        select(DagRun).where(DagRun.dag_id == dag_id)
        .order_by(DagRun.started_at.desc()).limit(20)
    )
    runs = runs_result.scalars().all()

    # Anomalies
    anomalies_result = await db.execute(
        select(Anomaly).where(Anomaly.dag_id == dag_id)
        .order_by(Anomaly.created_at.desc()).limit(50)
    )
    anomalies = anomalies_result.scalars().all()

    # Data sample
    data_result = await db.execute(
        select(PipelineData).where(PipelineData.dag_id == dag_id)
        .order_by(PipelineData.created_at.desc()).limit(10)
    )
    data_sample = [
        {"id": str(d.id), "run_id": d.run_id, "quarantined": d.is_quarantined, **d.record_data}
        for d in data_result.scalars().all()
    ]

    dag_response = DagResponse(
        id=dag.id, dag_id=dag.dag_id, name=dag.name, description=dag.description,
        schedule=dag.schedule, source_type=dag.source_type, status=dag.status,
        created_at=dag.created_at, updated_at=dag.updated_at,
        anomaly_count=anomaly_count, last_run_time=last_run_time,
    )

    return DagDetailResponse(
        dag=dag_response,
        recent_runs=[DagRunResponse.model_validate(r) for r in runs],
        anomalies=[AnomalyResponse.model_validate(a) for a in anomalies],
        data_sample=data_sample,
    )


@router.post("/pipelines/{dag_id}/scan", response_model=ScanResponse)
async def scan_pipeline(dag_id: str, db: AsyncSession = Depends(get_db)):
    dag_result = await db.execute(select(Dag).where(Dag.dag_id == dag_id))
    dag = dag_result.scalar_one_or_none()
    if not dag:
        raise HTTPException(status_code=404, detail="DAG not found")

    # Detect anomalies
    anomalies = await detector.scan_dag(db, dag_id)

    resolved_count = 0
    for anomaly in anomalies:
        # Auto-heal each anomaly
        audit = await healer.analyze_and_heal(db, anomaly)
        if audit.outcome == "success":
            resolved_count += 1
        # Publish SSE event
        await sse_manager.publish("anomaly", {
            "id": str(anomaly.id),
            "dag_id": anomaly.dag_id,
            "type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "description": anomaly.description,
            "status": anomaly.status,
            "action": anomaly.resolution_action,
        })

    await db.flush()

    return ScanResponse(
        dag_id=dag_id,
        anomalies_found=len(anomalies),
        anomalies_resolved=resolved_count,
        details=[AnomalyResponse.model_validate(a) for a in anomalies],
    )


@router.get("/alerts", response_model=list[AnomalyResponse])
async def list_alerts(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Anomaly).order_by(Anomaly.created_at.desc()).limit(100)
    if status:
        query = query.where(Anomaly.status == status)
    result = await db.execute(query)
    return [AnomalyResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/alerts/{alert_id}", response_model=AnomalyResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Anomaly).where(Anomaly.id == alert_id))
    anomaly = result.scalar_one_or_none()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AnomalyResponse.model_validate(anomaly)


@router.get("/audit", response_model=list[AuditLogResponse])
async def list_audit_log(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)
    )
    return [AuditLogResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/stream")
async def stream_alerts():
    async def event_generator():
        async for data in sse_manager.subscribe():
            yield {"data": data}

    return EventSourceResponse(event_generator())
