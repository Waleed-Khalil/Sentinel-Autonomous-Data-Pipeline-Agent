import type { Anomaly } from "../types";

const typeLabels: Record<string, string> = {
  schema_drift: "Schema Drift",
  null_spike: "Null Spike",
  statistical_anomaly: "Statistical Anomaly",
};

const actionLabels: Record<string, string> = {
  skip_bad_records: "Skip Bad Records",
  apply_defaults: "Apply Defaults",
  trigger_dag_retry: "Trigger DAG Retry",
  quarantine_records: "Quarantine Records",
};

const statusStyles: Record<string, string> = {
  detected: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30",
  resolved: "bg-green-500/10 text-green-400 border-green-500/30",
  failed: "bg-red-500/10 text-red-400 border-red-500/30",
};

export default function AnomalyDetail({ anomaly }: { anomaly: Anomaly }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {typeLabels[anomaly.anomaly_type] || anomaly.anomaly_type}
          </span>
          <p className="text-sm text-white mt-1">{anomaly.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs px-2 py-0.5 rounded border ${statusStyles[anomaly.status]}`}
          >
            {anomaly.status}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              anomaly.severity === "critical"
                ? "bg-red-500/10 text-red-400"
                : "bg-yellow-500/10 text-yellow-400"
            }`}
          >
            {anomaly.severity}
          </span>
        </div>
      </div>

      {anomaly.claude_reasoning && (
        <div className="bg-blue-950/20 border border-blue-500/20 rounded p-3">
          <div className="text-[10px] uppercase tracking-wide text-blue-400 mb-1 font-semibold">
            Claude's Reasoning
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">{anomaly.claude_reasoning}</p>
        </div>
      )}

      {anomaly.resolution_action && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Action taken:</span>
          <span className="text-xs font-medium bg-green-500/10 text-green-400 px-2 py-0.5 rounded">
            {actionLabels[anomaly.resolution_action] || anomaly.resolution_action}
          </span>
        </div>
      )}

      {anomaly.details && (
        <details className="text-xs">
          <summary className="text-gray-500 cursor-pointer hover:text-gray-300">
            Raw details
          </summary>
          <pre className="mt-2 bg-gray-950 rounded p-2 overflow-x-auto text-gray-400">
            {JSON.stringify(anomaly.details, null, 2)}
          </pre>
        </details>
      )}

      <div className="text-[10px] text-gray-600">
        Detected: {new Date(anomaly.created_at).toLocaleString()}
        {anomaly.resolved_at && ` | Resolved: ${new Date(anomaly.resolved_at).toLocaleString()}`}
      </div>
    </div>
  );
}
