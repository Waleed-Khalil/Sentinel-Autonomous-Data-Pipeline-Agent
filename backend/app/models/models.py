import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Dag(Base):
    __tablename__ = "dags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dag_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    schedule = Column(String(100), nullable=False)
    source_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="healthy")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class DagRun(Base):
    __tablename__ = "dag_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dag_id = Column(String(255), ForeignKey("dags.dag_id"), nullable=False)
    run_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="running")
    started_at = Column(DateTime(timezone=True), default=utcnow)
    finished_at = Column(DateTime(timezone=True))
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text)


class PipelineData(Base):
    __tablename__ = "pipeline_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dag_id = Column(String(255), ForeignKey("dags.dag_id"), nullable=False)
    run_id = Column(String(255), nullable=False)
    record_data = Column(JSONB, nullable=False)
    schema_version = Column(Integer, default=1)
    is_quarantined = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dag_id = Column(String(255), ForeignKey("dags.dag_id"), nullable=False)
    run_id = Column(String(255))
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False, default="warning")
    description = Column(Text, nullable=False)
    details = Column(JSONB)
    status = Column(String(50), nullable=False, default="detected")
    resolution = Column(Text)
    resolution_action = Column(String(100))
    claude_reasoning = Column(Text)
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anomaly_id = Column(UUID(as_uuid=True), ForeignKey("anomalies.id"))
    dag_id = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    reasoning = Column(Text, nullable=False)
    details = Column(JSONB)
    outcome = Column(String(50), nullable=False, default="pending")
    autonomous = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
