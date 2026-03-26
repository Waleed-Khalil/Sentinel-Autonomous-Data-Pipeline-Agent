import uuid
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import Anomaly, DagRun, PipelineData


class AnomalyDetector:
    """Detects schema drift, null spikes, and statistical anomalies in pipeline data."""

    async def scan_dag(self, db: AsyncSession, dag_id: str) -> list[Anomaly]:
        anomalies: list[Anomaly] = []

        # Get the latest run
        result = await db.execute(
            select(DagRun)
            .where(DagRun.dag_id == dag_id)
            .order_by(DagRun.started_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()
        if not latest_run:
            return anomalies

        # Get data for latest run
        result = await db.execute(
            select(PipelineData)
            .where(PipelineData.dag_id == dag_id, PipelineData.run_id == latest_run.run_id)
            .limit(1000)
        )
        latest_data = result.scalars().all()
        if not latest_data:
            return anomalies

        # Get data from previous run for comparison
        result = await db.execute(
            select(DagRun)
            .where(DagRun.dag_id == dag_id, DagRun.run_id != latest_run.run_id)
            .order_by(DagRun.started_at.desc())
            .limit(1)
        )
        prev_run = result.scalar_one_or_none()
        prev_data = []
        if prev_run:
            result = await db.execute(
                select(PipelineData)
                .where(PipelineData.dag_id == dag_id, PipelineData.run_id == prev_run.run_id)
                .limit(1000)
            )
            prev_data = result.scalars().all()

        # Run all three anomaly checks
        anomalies.extend(
            await self._detect_schema_drift(db, dag_id, latest_run.run_id, latest_data, prev_data)
        )
        anomalies.extend(
            await self._detect_null_spikes(db, dag_id, latest_run.run_id, latest_data)
        )
        anomalies.extend(
            await self._detect_statistical_anomalies(db, dag_id, latest_run.run_id, latest_data, prev_data)
        )

        for anomaly in anomalies:
            db.add(anomaly)
        await db.flush()

        return anomalies

    async def _detect_schema_drift(
        self, db: AsyncSession, dag_id: str, run_id: str,
        latest_data: list[PipelineData], prev_data: list[PipelineData]
    ) -> list[Anomaly]:
        if not prev_data or not latest_data:
            return []

        prev_keys = set()
        for rec in prev_data[:50]:
            prev_keys.update(rec.record_data.keys())

        curr_keys = set()
        curr_types: dict[str, set] = {}
        for rec in latest_data[:50]:
            curr_keys.update(rec.record_data.keys())
            for k, v in rec.record_data.items():
                curr_types.setdefault(k, set()).add(type(v).__name__)

        prev_types: dict[str, set] = {}
        for rec in prev_data[:50]:
            for k, v in rec.record_data.items():
                prev_types.setdefault(k, set()).add(type(v).__name__)

        anomalies = []

        added = curr_keys - prev_keys
        removed = prev_keys - curr_keys

        if added:
            anomalies.append(Anomaly(
                id=uuid.uuid4(),
                dag_id=dag_id, run_id=run_id,
                anomaly_type="schema_drift",
                severity="warning",
                description=f"New columns detected: {', '.join(sorted(added))}",
                details={"added_columns": sorted(added), "drift_type": "column_added"},
                status="detected",
            ))

        if removed:
            anomalies.append(Anomaly(
                id=uuid.uuid4(),
                dag_id=dag_id, run_id=run_id,
                anomaly_type="schema_drift",
                severity="critical",
                description=f"Columns removed: {', '.join(sorted(removed))}",
                details={"removed_columns": sorted(removed), "drift_type": "column_removed"},
                status="detected",
            ))

        # Type changes
        common = curr_keys & prev_keys
        for col in common:
            ct = curr_types.get(col, set())
            pt = prev_types.get(col, set())
            if ct and pt and ct != pt and "NoneType" not in ct and "NoneType" not in pt:
                anomalies.append(Anomaly(
                    id=uuid.uuid4(),
                    dag_id=dag_id, run_id=run_id,
                    anomaly_type="schema_drift",
                    severity="critical",
                    description=f"Column '{col}' type changed from {pt} to {ct}",
                    details={
                        "column": col, "drift_type": "type_changed",
                        "previous_types": sorted(pt), "current_types": sorted(ct),
                    },
                    status="detected",
                ))

        return anomalies

    async def _detect_null_spikes(
        self, db: AsyncSession, dag_id: str, run_id: str, data: list[PipelineData]
    ) -> list[Anomaly]:
        if not data:
            return []

        # Count nulls per column
        null_counts: dict[str, int] = {}
        total_counts: dict[str, int] = {}
        for rec in data:
            for k, v in rec.record_data.items():
                total_counts[k] = total_counts.get(k, 0) + 1
                if v is None:
                    null_counts[k] = null_counts.get(k, 0) + 1

        anomalies = []
        for col, total in total_counts.items():
            nulls = null_counts.get(col, 0)
            null_pct = nulls / total if total > 0 else 0
            if null_pct > settings.null_spike_threshold:
                severity = "critical" if null_pct > 0.5 else "warning"
                anomalies.append(Anomaly(
                    id=uuid.uuid4(),
                    dag_id=dag_id, run_id=run_id,
                    anomaly_type="null_spike",
                    severity=severity,
                    description=f"Column '{col}' has {null_pct:.1%} null values ({nulls}/{total})",
                    details={
                        "column": col, "null_count": nulls,
                        "total_count": total, "null_percentage": round(null_pct, 4),
                    },
                    status="detected",
                ))

        return anomalies

    async def _detect_statistical_anomalies(
        self, db: AsyncSession, dag_id: str, run_id: str,
        latest_data: list[PipelineData], prev_data: list[PipelineData]
    ) -> list[Anomaly]:
        if not prev_data or not latest_data:
            return []

        # Collect numeric columns from previous data to establish baseline
        baseline: dict[str, list[float]] = {}
        for rec in prev_data:
            for k, v in rec.record_data.items():
                if isinstance(v, (int, float)) and v is not None:
                    baseline.setdefault(k, []).append(float(v))

        anomalies = []
        threshold = settings.statistical_anomaly_std_devs

        for col, values in baseline.items():
            if len(values) < 5:
                continue
            mean = np.mean(values)
            std = np.std(values)
            if std == 0:
                continue

            # Check latest data for values outside expected range
            outlier_count = 0
            total = 0
            outlier_examples = []
            for rec in latest_data:
                v = rec.record_data.get(col)
                if isinstance(v, (int, float)) and v is not None:
                    total += 1
                    z_score = abs(v - mean) / std
                    if z_score > threshold:
                        outlier_count += 1
                        if len(outlier_examples) < 5:
                            outlier_examples.append({"value": v, "z_score": round(z_score, 2)})

            if total > 0 and outlier_count / total > 0.1:
                severity = "critical" if outlier_count / total > 0.3 else "warning"
                anomalies.append(Anomaly(
                    id=uuid.uuid4(),
                    dag_id=dag_id, run_id=run_id,
                    anomaly_type="statistical_anomaly",
                    severity=severity,
                    description=f"Column '{col}': {outlier_count}/{total} values outside {threshold}σ range (mean={mean:.2f}, std={std:.2f})",
                    details={
                        "column": col, "mean": round(mean, 4), "std": round(std, 4),
                        "outlier_count": outlier_count, "total_count": total,
                        "outlier_percentage": round(outlier_count / total, 4),
                        "examples": outlier_examples,
                    },
                    status="detected",
                ))

        return anomalies
