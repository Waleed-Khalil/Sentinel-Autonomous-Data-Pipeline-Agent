import { useApi } from "../hooks/useApi";
import type { Stats } from "../types";

export default function StatsBar() {
  const { data: stats } = useApi<Stats>("/stats");

  if (!stats) return null;

  const items = [
    { label: "Total DAGs", value: stats.total_dags, color: "text-blue-400" },
    { label: "Active Alerts", value: stats.active_alerts, color: stats.active_alerts > 0 ? "text-red-400" : "text-green-400" },
    { label: "Total Anomalies", value: stats.total_anomalies, color: "text-yellow-400" },
    { label: "Resolved", value: stats.resolved_anomalies, color: "text-green-400" },
    {
      label: "Resolution Rate",
      value: `${(stats.resolution_rate * 100).toFixed(1)}%`,
      color: stats.resolution_rate >= 0.85 ? "text-green-400" : "text-yellow-400",
    },
  ];

  return (
    <div className="grid grid-cols-5 gap-4">
      {items.map((item) => (
        <div key={item.label} className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
          <div className="text-xs text-gray-500 mt-1 uppercase tracking-wide">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
