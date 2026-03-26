import { useApi } from "../hooks/useApi";
import type { Anomaly } from "../types";
import AnomalyDetail from "../components/AnomalyDetail";

export default function Alerts() {
  const { data: anomalies, loading } = useApi<Anomaly[]>("/alerts");

  if (loading) return <div className="text-gray-600 text-center py-12">Loading alerts...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white">All Alerts</h1>
      {!anomalies || anomalies.length === 0 ? (
        <div className="text-gray-600 text-center py-12 bg-gray-900 border border-gray-800 rounded-lg">
          No alerts detected
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.map((a) => (
            <AnomalyDetail key={a.id} anomaly={a} />
          ))}
        </div>
      )}
    </div>
  );
}
