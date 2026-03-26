export interface Pipeline {
  id: string;
  dag_id: string;
  name: string;
  description: string | null;
  schedule: string;
  source_type: string;
  status: "healthy" | "warning" | "critical";
  created_at: string;
  updated_at: string;
  anomaly_count: number;
  last_run_time: string | null;
}

export interface DagRun {
  id: string;
  dag_id: string;
  run_id: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  records_processed: number;
  records_failed: number;
  error_message: string | null;
}

export interface Anomaly {
  id: string;
  dag_id: string;
  run_id: string | null;
  anomaly_type: "schema_drift" | "null_spike" | "statistical_anomaly";
  severity: "warning" | "critical";
  description: string;
  details: Record<string, unknown> | null;
  status: "detected" | "resolved" | "failed";
  resolution: string | null;
  resolution_action: string | null;
  claude_reasoning: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface AuditEntry {
  id: string;
  anomaly_id: string | null;
  dag_id: string;
  action: string;
  reasoning: string;
  details: Record<string, unknown> | null;
  outcome: string;
  autonomous: boolean;
  created_at: string;
}

export interface PipelineDetail {
  dag: Pipeline;
  recent_runs: DagRun[];
  anomalies: Anomaly[];
  data_sample: Record<string, unknown>[];
}

export interface Stats {
  total_dags: number;
  active_alerts: number;
  total_anomalies: number;
  resolved_anomalies: number;
  resolution_rate: number;
}

export interface SSEAlert {
  event: string;
  data: {
    id: string;
    dag_id: string;
    type: string;
    severity: string;
    description: string;
    status: string;
    action: string;
  };
  timestamp: string;
}
