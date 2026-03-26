import asyncio
import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session
from app.models.models import Dag
from app.services.anomaly_detector import AnomalyDetector
from app.services.claude_healer import ClaudeHealer
from app.services.sse_manager import sse_manager

logger = logging.getLogger("sentinel.scanner")


class BackgroundScanner:
    """Continuously scans all DAGs for anomalies and triggers self-healing."""

    def __init__(self):
        self.detector = AnomalyDetector()
        self.healer = ClaudeHealer()
        self.interval = settings.scan_interval_seconds

    async def run(self):
        logger.info("Background scanner started (interval=%ds)", self.interval)
        # Wait for DB to be ready
        await asyncio.sleep(5)

        while True:
            try:
                await self._scan_all()
            except Exception as e:
                logger.error("Scanner error: %s", e)
            await asyncio.sleep(self.interval)

    async def _scan_all(self):
        async with async_session() as db:
            result = await db.execute(select(Dag))
            dags = result.scalars().all()

            for dag in dags:
                try:
                    anomalies = await self.detector.scan_dag(db, dag.dag_id)
                    for anomaly in anomalies:
                        audit = await self.healer.analyze_and_heal(db, anomaly)
                        await sse_manager.publish("anomaly", {
                            "id": str(anomaly.id),
                            "dag_id": anomaly.dag_id,
                            "type": anomaly.anomaly_type,
                            "severity": anomaly.severity,
                            "description": anomaly.description,
                            "status": anomaly.status,
                            "action": anomaly.resolution_action,
                        })
                    await db.commit()
                except Exception as e:
                    logger.error("Error scanning DAG %s: %s", dag.dag_id, e)
                    await db.rollback()
