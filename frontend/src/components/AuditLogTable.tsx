import { useApi } from "../hooks/useApi";
import type { AuditEntry } from "../types";

const actionLabels: Record<string, string> = {
  skip_bad_records: "Skip Bad Records",
  apply_defaults: "Apply Defaults",
  trigger_dag_retry: "Trigger Retry",
  quarantine_records: "Quarantine",
};

export default function AuditLogTable() {
  const { data: entries, loading } = useApi<AuditEntry[]>("/audit");

  if (loading) return <div className="text-center text-gray-600 py-8">Loading audit log...</div>;
  if (!entries || entries.length === 0) return <div className="text-center text-gray-600 py-8">No audit entries yet</div>;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
            <th className="text-left px-4 py-3">Time</th>
            <th className="text-left px-4 py-3">DAG</th>
            <th className="text-left px-4 py-3">Action</th>
            <th className="text-left px-4 py-3">Reasoning</th>
            <th className="text-left px-4 py-3">Outcome</th>
            <th className="text-left px-4 py-3">Mode</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
              <td className="px-4 py-2 text-xs text-gray-500 whitespace-nowrap">
                {new Date(entry.created_at).toLocaleString()}
              </td>
              <td className="px-4 py-2 text-xs font-medium text-gray-300">
                {entry.dag_id}
              </td>
              <td className="px-4 py-2">
                <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">
                  {actionLabels[entry.action] || entry.action}
                </span>
              </td>
              <td className="px-4 py-2 text-xs text-gray-400 max-w-xs truncate">
                {entry.reasoning}
              </td>
              <td className="px-4 py-2">
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    entry.outcome === "success"
                      ? "bg-green-500/10 text-green-400"
                      : "bg-red-500/10 text-red-400"
                  }`}
                >
                  {entry.outcome}
                </span>
              </td>
              <td className="px-4 py-2">
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                    entry.autonomous
                      ? "bg-blue-500/10 text-blue-400"
                      : "bg-gray-700 text-gray-400"
                  }`}
                >
                  {entry.autonomous ? "Autonomous" : "Manual"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
