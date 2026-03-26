import json
import uuid
from datetime import datetime, timezone

import anthropic
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import Anomaly, AuditLog, Dag, PipelineData


HEALING_PROMPT = """You are Sentinel, an autonomous data pipeline monitoring agent. You've detected an anomaly in a data pipeline and must decide on the best remediation action.

ANOMALY DETAILS:
- DAG: {dag_id}
- Type: {anomaly_type}
- Severity: {severity}
- Description: {description}
- Details: {details}

AVAILABLE ACTIONS:
1. skip_bad_records — Remove/skip records that contain the anomalous data. Best for: isolated bad records, small percentage of failures.
2. apply_defaults — Replace null/missing values with sensible defaults. Best for: null spikes where data is expected to exist.
3. trigger_dag_retry — Retry the entire DAG run. Best for: transient failures, upstream issues that may have been resolved.
4. quarantine_records — Move anomalous records to quarantine for manual review. Best for: critical schema changes, large-scale data quality issues.

Respond with EXACTLY this JSON format:
{{
  "action": "<one of: skip_bad_records, apply_defaults, trigger_dag_retry, quarantine_records>",
  "reasoning": "<2-3 sentence explanation of why this action was chosen>",
  "confidence": <float 0.0-1.0>,
  "details": {{<any additional context about the remediation>}}
}}"""


class ClaudeHealer:
    """Uses Claude API to analyze anomalies and apply self-healing actions."""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def analyze_and_heal(self, db: AsyncSession, anomaly: Anomaly) -> AuditLog:
        # Get Claude's analysis
        decision = await self._get_claude_decision(anomaly)

        action = decision.get("action", "quarantine_records")
        reasoning = decision.get("reasoning", "Fallback: quarantining for manual review.")
        confidence = decision.get("confidence", 0.5)

        # Apply the healing action
        outcome = await self._apply_action(db, anomaly, action)

        # Update the anomaly record
        anomaly.status = "resolved" if outcome == "success" else "failed"
        anomaly.resolution = reasoning
        anomaly.resolution_action = action
        anomaly.claude_reasoning = reasoning
        anomaly.resolved_at = datetime.now(timezone.utc) if outcome == "success" else None

        # Update DAG status
        await self._update_dag_status(db, anomaly.dag_id)

        # Create audit log entry
        audit = AuditLog(
            id=uuid.uuid4(),
            anomaly_id=anomaly.id,
            dag_id=anomaly.dag_id,
            action=action,
            reasoning=reasoning,
            details={
                "confidence": confidence,
                "anomaly_type": anomaly.anomaly_type,
                "severity": anomaly.severity,
                **decision.get("details", {}),
            },
            outcome=outcome,
            autonomous=True,
        )
        db.add(audit)
        return audit

    async def _get_claude_decision(self, anomaly: Anomaly) -> dict:
        prompt = HEALING_PROMPT.format(
            dag_id=anomaly.dag_id,
            anomaly_type=anomaly.anomaly_type,
            severity=anomaly.severity,
            description=anomaly.description,
            details=json.dumps(anomaly.details or {}, indent=2),
        )

        try:
            response = await self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            # Fallback decision if Claude API fails
            return self._fallback_decision(anomaly)

        return self._fallback_decision(anomaly)

    def _fallback_decision(self, anomaly: Anomaly) -> dict:
        """Rule-based fallback when Claude API is unavailable."""
        if anomaly.anomaly_type == "null_spike":
            null_pct = (anomaly.details or {}).get("null_percentage", 0)
            if null_pct > 0.5:
                return {
                    "action": "quarantine_records",
                    "reasoning": f"High null rate ({null_pct:.0%}) suggests systemic data issue. Quarantining for review.",
                    "confidence": 0.7,
                    "details": {"fallback": True},
                }
            return {
                "action": "apply_defaults",
                "reasoning": f"Moderate null rate ({null_pct:.0%}). Applying default values to maintain pipeline flow.",
                "confidence": 0.8,
                "details": {"fallback": True},
            }
        elif anomaly.anomaly_type == "schema_drift":
            drift_type = (anomaly.details or {}).get("drift_type", "")
            if drift_type == "column_removed":
                return {
                    "action": "quarantine_records",
                    "reasoning": "Column removal detected — quarantining records until schema is verified.",
                    "confidence": 0.75,
                    "details": {"fallback": True},
                }
            return {
                "action": "skip_bad_records",
                "reasoning": "Schema drift detected with added columns. Skipping records with unexpected schema.",
                "confidence": 0.8,
                "details": {"fallback": True},
            }
        elif anomaly.anomaly_type == "statistical_anomaly":
            outlier_pct = (anomaly.details or {}).get("outlier_percentage", 0)
            if outlier_pct > 0.3:
                return {
                    "action": "quarantine_records",
                    "reasoning": f"High outlier rate ({outlier_pct:.0%}). Quarantining anomalous records for investigation.",
                    "confidence": 0.7,
                    "details": {"fallback": True},
                }
            return {
                "action": "skip_bad_records",
                "reasoning": "Statistical outliers detected. Skipping anomalous records to maintain data quality.",
                "confidence": 0.8,
                "details": {"fallback": True},
            }

        return {
            "action": "trigger_dag_retry",
            "reasoning": "Unknown anomaly type. Retrying DAG as a safe default action.",
            "confidence": 0.5,
            "details": {"fallback": True},
        }

    async def _apply_action(self, db: AsyncSession, anomaly: Anomaly, action: str) -> str:
        try:
            if action == "skip_bad_records":
                await self._skip_bad_records(db, anomaly)
            elif action == "apply_defaults":
                await self._apply_defaults(db, anomaly)
            elif action == "trigger_dag_retry":
                await self._trigger_retry(db, anomaly)
            elif action == "quarantine_records":
                await self._quarantine_records(db, anomaly)
            return "success"
        except Exception as e:
            return f"failed: {str(e)}"

    async def _skip_bad_records(self, db: AsyncSession, anomaly: Anomaly):
        """Mark bad records as quarantined (effectively skipping them)."""
        col = (anomaly.details or {}).get("column")
        if not col or not anomaly.run_id:
            return
        # Find records with null/bad values in the offending column and quarantine them
        from sqlalchemy import select
        result = await db.execute(
            select(PipelineData).where(
                PipelineData.dag_id == anomaly.dag_id,
                PipelineData.run_id == anomaly.run_id,
                PipelineData.is_quarantined == False,
            )
        )
        records = result.scalars().all()
        skipped = 0
        for rec in records:
            val = rec.record_data.get(col)
            if val is None or (anomaly.anomaly_type == "statistical_anomaly"):
                rec.is_quarantined = True
                skipped += 1
                if skipped >= 50:
                    break

    async def _apply_defaults(self, db: AsyncSession, anomaly: Anomaly):
        """Replace null values with sensible defaults."""
        col = (anomaly.details or {}).get("column")
        if not col or not anomaly.run_id:
            return
        from sqlalchemy import select
        result = await db.execute(
            select(PipelineData).where(
                PipelineData.dag_id == anomaly.dag_id,
                PipelineData.run_id == anomaly.run_id,
            )
        )
        records = result.scalars().all()
        # Collect non-null values to compute a default
        non_null_vals = [
            rec.record_data.get(col) for rec in records
            if rec.record_data.get(col) is not None
        ]
        if not non_null_vals:
            default = 0
        elif isinstance(non_null_vals[0], (int, float)):
            default = round(sum(non_null_vals) / len(non_null_vals), 2)
        elif isinstance(non_null_vals[0], str):
            default = "N/A"
        else:
            default = None

        for rec in records:
            if rec.record_data.get(col) is None:
                data = dict(rec.record_data)
                data[col] = default
                rec.record_data = data

    async def _trigger_retry(self, db: AsyncSession, anomaly: Anomaly):
        """Simulate a DAG retry by creating a new run entry."""
        from app.models.models import DagRun
        new_run = DagRun(
            id=uuid.uuid4(),
            dag_id=anomaly.dag_id,
            run_id=f"{anomaly.dag_id}_retry_{uuid.uuid4().hex[:8]}",
            status="success",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            records_processed=100,
            records_failed=0,
        )
        db.add(new_run)

    async def _quarantine_records(self, db: AsyncSession, anomaly: Anomaly):
        """Quarantine all records from the anomalous run."""
        if not anomaly.run_id:
            return
        from sqlalchemy import select
        result = await db.execute(
            select(PipelineData).where(
                PipelineData.dag_id == anomaly.dag_id,
                PipelineData.run_id == anomaly.run_id,
                PipelineData.is_quarantined == False,
            )
        )
        records = result.scalars().all()
        for rec in records:
            rec.is_quarantined = True

    async def _update_dag_status(self, db: AsyncSession, dag_id: str):
        """Update DAG status based on unresolved anomalies."""
        from sqlalchemy import select, func
        result = await db.execute(
            select(func.count()).where(
                Anomaly.dag_id == dag_id,
                Anomaly.status == "detected",
            )
        )
        unresolved = result.scalar()
        if unresolved == 0:
            status = "healthy"
        elif unresolved <= 2:
            status = "warning"
        else:
            status = "critical"

        await db.execute(
            update(Dag).where(Dag.dag_id == dag_id).values(
                status=status, updated_at=datetime.now(timezone.utc)
            )
        )
