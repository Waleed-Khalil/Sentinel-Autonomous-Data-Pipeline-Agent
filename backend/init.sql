CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- DAG definitions
CREATE TABLE IF NOT EXISTS dags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dag_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    schedule VARCHAR(100) NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'healthy',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- DAG run history
CREATE TABLE IF NOT EXISTS dag_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dag_id VARCHAR(255) NOT NULL REFERENCES dags(dag_id),
    run_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT
);

-- Simulated pipeline data (represents data flowing through DAGs)
CREATE TABLE IF NOT EXISTS pipeline_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dag_id VARCHAR(255) NOT NULL REFERENCES dags(dag_id),
    run_id VARCHAR(255) NOT NULL,
    record_data JSONB NOT NULL,
    schema_version INTEGER DEFAULT 1,
    is_quarantined BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Detected anomalies
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dag_id VARCHAR(255) NOT NULL REFERENCES dags(dag_id),
    run_id VARCHAR(255),
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL DEFAULT 'warning',
    description TEXT NOT NULL,
    details JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'detected',
    resolution TEXT,
    resolution_action VARCHAR(100),
    claude_reasoning TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for all autonomous decisions
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anomaly_id UUID REFERENCES anomalies(id),
    dag_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    reasoning TEXT NOT NULL,
    details JSONB,
    outcome VARCHAR(50) NOT NULL DEFAULT 'pending',
    autonomous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dag_runs_dag_id ON dag_runs(dag_id);
CREATE INDEX IF NOT EXISTS idx_dag_runs_status ON dag_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_data_dag_id ON pipeline_data(dag_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_dag_id ON anomalies(dag_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_dag_id ON audit_log(dag_id);
