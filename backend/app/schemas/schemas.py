from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class DagResponse(BaseModel):
    id: UUID
    dag_id: str
    name: str
    description: Optional[str]
    schedule: str
    source_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    anomaly_count: int = 0
    last_run_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class DagRunResponse(BaseModel):
    id: UUID
    dag_id: str
    run_id: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    records_processed: int
    records_failed: int
    error_message: Optional[str]

    class Config:
        from_attributes = True


class DagDetailResponse(BaseModel):
    dag: DagResponse
    recent_runs: list[DagRunResponse]
    anomalies: list["AnomalyResponse"]
    data_sample: list[dict[str, Any]]


class AnomalyResponse(BaseModel):
    id: UUID
    dag_id: str
    run_id: Optional[str]
    anomaly_type: str
    severity: str
    description: str
    details: Optional[dict[str, Any]]
    status: str
    resolution: Optional[str]
    resolution_action: Optional[str]
    claude_reasoning: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: UUID
    anomaly_id: Optional[UUID]
    dag_id: str
    action: str
    reasoning: str
    details: Optional[dict[str, Any]]
    outcome: str
    autonomous: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    dag_id: str
    anomalies_found: int
    anomalies_resolved: int
    details: list[AnomalyResponse]


class StatsResponse(BaseModel):
    total_dags: int
    active_alerts: int
    total_anomalies: int
    resolved_anomalies: int
    resolution_rate: float
