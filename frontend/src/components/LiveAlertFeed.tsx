import type { SSEAlert } from "../types";

const severityColors = {
  warning: "border-l-yellow-400 bg-yellow-950/20",
  critical: "border-l-red-400 bg-red-950/20",
};

const actionLabels: Record<string, string> = {
  skip_bad_records: "Skipped bad records",
  apply_defaults: "Applied defaults",
  trigger_dag_retry: "Triggered retry",
  quarantine_records: "Quarantined records",
};

export default function LiveAlertFeed({ alerts }: { alerts: SSEAlert[] }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400">Live Alert Feed</h2>
      </div>
      <div className="max-h-[600px] overflow-y-auto scrollbar-thin">
        {alerts.length === 0 ? (
          <div className="p-4 text-center text-gray-600 text-sm">
            Waiting for alerts...
          </div>
        ) : (
          alerts.map((alert, i) => (
            <div
              key={`${alert.data.id}-${i}`}
              className={`border-l-2 px-3 py-2 border-b border-gray-800/50 ${severityColors[alert.data.severity as keyof typeof severityColors] || "border-l-gray-500"}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-300">{alert.data.dag_id}</span>
                <span className="text-[10px] text-gray-600">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-1 line-clamp-2">{alert.data.description}</p>
              {alert.data.action && (
                <span className="inline-block text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-400">
                  {actionLabels[alert.data.action] || alert.data.action}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
