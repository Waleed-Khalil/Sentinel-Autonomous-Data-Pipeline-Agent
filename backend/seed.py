#!/usr/bin/env python3
"""
Seed script for Sentinel — populates the database with 12 realistic DAGs,
simulated pipeline data, and injected failures for anomaly detection.

Usage: python seed.py
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import Json

DATABASE_URL = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://sentinel:sentinel@localhost:5432/sentinel",
)

# --- DAG Definitions ---
DAGS = [
    {
        "dag_id": "etl_user_events",
        "name": "User Events ETL",
        "description": "Ingests user clickstream and interaction events from web/mobile",
        "schedule": "*/15 * * * *",
        "source_type": "Kafka",
    },
    {
        "dag_id": "etl_transactions",
        "name": "Transaction Processing",
        "description": "Processes financial transactions from payment gateway",
        "schedule": "*/5 * * * *",
        "source_type": "PostgreSQL",
    },
    {
        "dag_id": "etl_inventory_sync",
        "name": "Inventory Sync",
        "description": "Synchronizes product inventory across warehouses",
        "schedule": "0 * * * *",
        "source_type": "REST API",
    },
    {
        "dag_id": "etl_customer_profiles",
        "name": "Customer Profile Enrichment",
        "description": "Enriches customer profiles with third-party demographic data",
        "schedule": "0 2 * * *",
        "source_type": "S3",
    },
    {
        "dag_id": "etl_log_aggregation",
        "name": "Log Aggregation Pipeline",
        "description": "Aggregates application logs for monitoring and alerting",
        "schedule": "*/10 * * * *",
        "source_type": "Filebeat",
    },
    {
        "dag_id": "etl_marketing_campaigns",
        "name": "Marketing Campaign Analytics",
        "description": "Processes campaign performance metrics and attribution data",
        "schedule": "0 6 * * *",
        "source_type": "Google Ads API",
    },
    {
        "dag_id": "etl_sensor_data",
        "name": "IoT Sensor Ingestion",
        "description": "Ingests temperature, humidity, and pressure readings from IoT sensors",
        "schedule": "*/2 * * * *",
        "source_type": "MQTT",
    },
    {
        "dag_id": "etl_order_fulfillment",
        "name": "Order Fulfillment Tracker",
        "description": "Tracks order status updates from fulfillment centers",
        "schedule": "*/30 * * * *",
        "source_type": "Webhook",
    },
    {
        "dag_id": "etl_product_reviews",
        "name": "Product Review Aggregator",
        "description": "Collects and processes product reviews from multiple platforms",
        "schedule": "0 4 * * *",
        "source_type": "Web Scraper",
    },
    {
        "dag_id": "etl_fraud_detection",
        "name": "Fraud Detection Features",
        "description": "Generates real-time features for the fraud detection ML model",
        "schedule": "*/5 * * * *",
        "source_type": "Kafka",
    },
    {
        "dag_id": "etl_email_events",
        "name": "Email Event Processing",
        "description": "Processes email delivery, open, and click events",
        "schedule": "*/15 * * * *",
        "source_type": "SendGrid API",
    },
    {
        "dag_id": "etl_data_warehouse",
        "name": "Data Warehouse Refresh",
        "description": "Full refresh of the analytics data warehouse tables",
        "schedule": "0 1 * * *",
        "source_type": "Multiple",
    },
]

# --- Schema definitions per DAG (for realistic data generation) ---
SCHEMAS = {
    "etl_user_events": {
        "user_id": lambda: f"usr_{random.randint(1000, 9999)}",
        "event_type": lambda: random.choice(["click", "view", "scroll", "purchase", "signup"]),
        "page_url": lambda: f"/page/{random.choice(['home', 'product', 'cart', 'checkout', 'profile'])}",
        "session_duration": lambda: round(random.gauss(120, 30), 1),
        "device": lambda: random.choice(["desktop", "mobile", "tablet"]),
    },
    "etl_transactions": {
        "transaction_id": lambda: f"txn_{uuid.uuid4().hex[:12]}",
        "amount": lambda: round(random.gauss(85, 25), 2),
        "currency": lambda: "USD",
        "status": lambda: random.choice(["completed", "pending", "completed", "completed"]),
        "merchant_id": lambda: f"merch_{random.randint(100, 500)}",
    },
    "etl_inventory_sync": {
        "product_id": lambda: f"prod_{random.randint(1, 200)}",
        "warehouse": lambda: random.choice(["US-East", "US-West", "EU-Central", "APAC"]),
        "quantity": lambda: random.randint(0, 500),
        "reorder_point": lambda: random.randint(10, 50),
        "last_restocked": lambda: (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
    },
    "etl_customer_profiles": {
        "customer_id": lambda: f"cust_{random.randint(10000, 99999)}",
        "age": lambda: random.randint(18, 75),
        "income_bracket": lambda: random.choice(["low", "medium", "high", "very_high"]),
        "location": lambda: random.choice(["New York", "San Francisco", "Chicago", "Austin", "Seattle"]),
        "lifetime_value": lambda: round(random.gauss(500, 150), 2),
    },
    "etl_log_aggregation": {
        "service": lambda: random.choice(["api-gateway", "auth-service", "user-service", "payment-service"]),
        "level": lambda: random.choice(["INFO", "INFO", "WARN", "ERROR", "INFO"]),
        "message": lambda: random.choice(["Request processed", "Cache miss", "Timeout warning", "Connection reset"]),
        "response_time_ms": lambda: round(random.gauss(45, 15), 1),
        "status_code": lambda: random.choice([200, 200, 200, 201, 400, 500]),
    },
    "etl_marketing_campaigns": {
        "campaign_id": lambda: f"camp_{random.randint(1, 50)}",
        "impressions": lambda: random.randint(1000, 50000),
        "clicks": lambda: random.randint(10, 500),
        "conversions": lambda: random.randint(0, 50),
        "spend": lambda: round(random.gauss(250, 80), 2),
    },
    "etl_sensor_data": {
        "sensor_id": lambda: f"sensor_{random.randint(1, 100)}",
        "temperature": lambda: round(random.gauss(22, 3), 2),
        "humidity": lambda: round(random.gauss(45, 10), 2),
        "pressure": lambda: round(random.gauss(1013, 5), 2),
        "battery_level": lambda: round(random.uniform(0.1, 1.0), 2),
    },
    "etl_order_fulfillment": {
        "order_id": lambda: f"ord_{uuid.uuid4().hex[:10]}",
        "status": lambda: random.choice(["packed", "shipped", "in_transit", "delivered"]),
        "carrier": lambda: random.choice(["UPS", "FedEx", "USPS", "DHL"]),
        "weight_kg": lambda: round(random.gauss(2.5, 1.0), 2),
        "delivery_days": lambda: random.randint(1, 7),
    },
    "etl_product_reviews": {
        "product_id": lambda: f"prod_{random.randint(1, 200)}",
        "rating": lambda: random.randint(1, 5),
        "review_length": lambda: random.randint(10, 500),
        "sentiment_score": lambda: round(random.gauss(0.6, 0.2), 3),
        "verified_purchase": lambda: random.choice([True, True, True, False]),
    },
    "etl_fraud_detection": {
        "transaction_id": lambda: f"txn_{uuid.uuid4().hex[:12]}",
        "risk_score": lambda: round(random.gauss(0.15, 0.1), 4),
        "velocity_1h": lambda: random.randint(1, 20),
        "amount": lambda: round(random.gauss(120, 60), 2),
        "is_flagged": lambda: random.choice([False, False, False, False, True]),
    },
    "etl_email_events": {
        "email_id": lambda: f"email_{uuid.uuid4().hex[:10]}",
        "event": lambda: random.choice(["delivered", "opened", "clicked", "bounced", "unsubscribed"]),
        "recipient_domain": lambda: random.choice(["gmail.com", "yahoo.com", "outlook.com", "company.com"]),
        "campaign_id": lambda: f"camp_{random.randint(1, 20)}",
        "open_rate": lambda: round(random.gauss(0.25, 0.08), 3),
    },
    "etl_data_warehouse": {
        "table_name": lambda: random.choice(["dim_users", "fact_orders", "dim_products", "fact_events"]),
        "rows_updated": lambda: random.randint(100, 10000),
        "duration_sec": lambda: round(random.gauss(300, 60), 1),
        "status": lambda: random.choice(["success", "success", "success", "partial"]),
        "data_freshness_hours": lambda: round(random.gauss(2, 0.5), 1),
    },
}


def generate_record(dag_id: str, inject_failure: str = None) -> dict:
    """Generate a single data record, optionally injecting a failure."""
    schema = SCHEMAS[dag_id]
    record = {}
    for col, gen in schema.items():
        record[col] = gen()

    if inject_failure == "null_spike":
        # Set 2-3 columns to None
        cols = list(record.keys())
        for col in random.sample(cols, min(3, len(cols))):
            record[col] = None

    elif inject_failure == "statistical_anomaly":
        # Inject extreme values in numeric columns
        for col, val in record.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                record[col] = val * random.choice([10, 15, -5, 20])

    elif inject_failure == "schema_drift_add":
        record["_extra_column"] = "unexpected_value"
        record["_metadata_v2"] = random.randint(1, 100)

    elif inject_failure == "schema_drift_remove":
        cols = list(record.keys())
        if len(cols) > 2:
            del record[cols[0]]

    elif inject_failure == "schema_drift_type":
        for col, val in list(record.items()):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                record[col] = str(val) + "_corrupted"
                break

    return record


def seed():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Clearing existing data...")
    for table in ["audit_log", "anomalies", "pipeline_data", "dag_runs", "dags"]:
        cur.execute(f"DELETE FROM {table}")

    print("Seeding DAGs...")
    now = datetime.now(timezone.utc)

    for dag_def in DAGS:
        cur.execute(
            """INSERT INTO dags (id, dag_id, name, description, schedule, source_type, status, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                str(uuid.uuid4()), dag_def["dag_id"], dag_def["name"],
                dag_def["description"], dag_def["schedule"], dag_def["source_type"],
                "healthy", now - timedelta(days=30), now,
            ),
        )

    print("Seeding DAG runs and pipeline data...")

    # Failure injection plan — ensures enough anomalies to demonstrate 85%+ resolution
    failure_plan = {
        "etl_user_events": ["null_spike"],
        "etl_transactions": ["statistical_anomaly"],
        "etl_inventory_sync": ["schema_drift_add"],
        "etl_customer_profiles": ["null_spike", "statistical_anomaly"],
        "etl_log_aggregation": [],
        "etl_marketing_campaigns": ["schema_drift_type"],
        "etl_sensor_data": ["statistical_anomaly"],
        "etl_order_fulfillment": ["null_spike"],
        "etl_product_reviews": [],
        "etl_fraud_detection": ["schema_drift_remove", "null_spike"],
        "etl_email_events": ["statistical_anomaly"],
        "etl_data_warehouse": ["schema_drift_add"],
    }

    for dag_def in DAGS:
        dag_id = dag_def["dag_id"]
        failures = failure_plan.get(dag_id, [])

        # Generate 3-5 historical runs
        num_runs = random.randint(3, 5)
        for run_idx in range(num_runs):
            run_id = f"{dag_id}_run_{run_idx + 1}"
            run_start = now - timedelta(hours=(num_runs - run_idx) * 4)
            is_latest = run_idx == num_runs - 1

            # Determine if this run should have failures
            run_failures = failures if is_latest else []
            records_per_run = random.randint(80, 150)
            failed_count = 0

            status = "success"
            error_msg = None

            if is_latest and failures:
                status = "failed"
                error_msg = f"Anomaly detected: {', '.join(failures)}"

            cur.execute(
                """INSERT INTO dag_runs (id, dag_id, run_id, status, started_at, finished_at,
                   records_processed, records_failed, error_message)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(uuid.uuid4()), dag_id, run_id, status,
                    run_start, run_start + timedelta(minutes=random.randint(2, 15)),
                    records_per_run, 0, error_msg,
                ),
            )

            # Generate pipeline data records
            for i in range(records_per_run):
                failure_type = None
                if run_failures and random.random() < 0.4:
                    failure_type = random.choice(run_failures)
                    failed_count += 1

                record = generate_record(dag_id, inject_failure=failure_type)

                cur.execute(
                    """INSERT INTO pipeline_data (id, dag_id, run_id, record_data, schema_version, is_quarantined, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        str(uuid.uuid4()), dag_id, run_id, Json(record),
                        1 if not failure_type else 2 if "schema" in (failure_type or "") else 1,
                        False, run_start + timedelta(seconds=i),
                    ),
                )

            # Update failed count
            if failed_count > 0:
                cur.execute(
                    "UPDATE dag_runs SET records_failed = %s WHERE run_id = %s",
                    (failed_count, run_id),
                )

        # Set DAG status based on failure plan
        if failures:
            dag_status = "critical" if len(failures) > 1 else "warning"
            cur.execute(
                "UPDATE dags SET status = %s, updated_at = %s WHERE dag_id = %s",
                (dag_status, now, dag_id),
            )

    cur.close()
    conn.close()

    print(f"Seeded {len(DAGS)} DAGs with pipeline data and injected failures.")
    print("\nFailure injection summary:")
    for dag_id, failures in failure_plan.items():
        status = "clean" if not failures else ", ".join(failures)
        print(f"  {dag_id}: {status}")
    print("\nDone! Run the API and trigger scans to see self-healing in action.")


if __name__ == "__main__":
    seed()
