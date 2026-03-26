import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useApi, postApi } from "../hooks/useApi";
import type { PipelineDetail as PipelineDetailType } from "../types";
import AnomalyDetail from "../components/AnomalyDetail";

const statusColors = {
  healthy: "text-green-400",
  warning: "text-yellow-400",
  critical: "text-red-400",
};

export default function PipelineDetailPage() {
  const { dagId } = useParams<{ dagId: string }>();
  const { data, loading, refetch } = useApi<PipelineDetailType>(`/pipelines/${dagId}`);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<string | null>(null);

  const handleScan = async () => {
    setScanning(true);
    setScanResult(null);
    try {
      const result = await postApi<{ anomalies_found: number; anomalies_resolved: number }>(
        `/pipelines/${dagId}/scan`
      );
      setScanResult(
        `Found ${result.anomalies_found} anomalies, resolved ${result.anomalies_resolved}`
      );
      refetch();
    } catch (e) {
      setScanResult("Scan failed");
    } finally {
      setScanning(false);
    }
  };

  if (loading || !data) {
    return <div className="text-gray-600 text-center py-12">Loading...</div>;
  }

  const { dag, recent_runs, anomalies, data_sample } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/" className="text-xs text-gray-500 hover:text-gray-300">
            &larr; Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-white mt-1">{dag.name}</h1>
          <p className="text-sm text-gray-500">{dag.dag_id} &middot; {dag.source_type} &middot; {dag.schedule}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-semibold capitalize ${statusColors[dag.status]}`}>
            {dag.status}
          </span>
          <button
            onClick={handleScan}
            disabled={scanning}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white text-sm px-4 py-2 rounded-lg transition"
          >
            {scanning ? "Scanning..." : "Trigger Scan"}
          </button>
        </div>
      </div>

      {scanResult && (
        <div className="bg-blue-950/30 border border-blue-500/30 rounded-lg px-4 py-2 text-sm text-blue-300">
          {scanResult}
        </div>
      )}

      {dag.description && (
        <p className="text-sm text-gray-400">{dag.description}</p>
      )}

      {/* Run History */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Recent Runs</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
                <th className="text-left px-4 py-2">Run ID</th>
                <th className="text-left px-4 py-2">Status</th>
                <th className="text-left px-4 py-2">Started</th>
                <th className="text-left px-4 py-2">Records</th>
                <th className="text-left px-4 py-2">Failed</th>
              </tr>
            </thead>
            <tbody>
              {recent_runs.map((run) => (
                <tr key={run.run_id} className="border-b border-gray-800/50">
                  <td className="px-4 py-2 text-xs font-mono text-gray-400">{run.run_id}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        run.status === "success"
                          ? "bg-green-500/10 text-green-400"
                          : run.status === "failed"
                          ? "bg-red-500/10 text-red-400"
                          : "bg-yellow-500/10 text-yellow-400"
                      }`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-500">
                    {new Date(run.started_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-400">{run.records_processed}</td>
                  <td className="px-4 py-2 text-xs text-red-400">{run.records_failed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Anomalies */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">
          Anomalies ({anomalies.length})
        </h2>
        {anomalies.length === 0 ? (
          <div className="text-gray-600 text-center py-8 bg-gray-900 border border-gray-800 rounded-lg">
            No anomalies detected
          </div>
        ) : (
          <div className="space-y-3">
            {anomalies.map((a) => (
              <AnomalyDetail key={a.id} anomaly={a} />
            ))}
          </div>
        )}
      </div>

      {/* Data Sample */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Data Sample</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-x-auto">
          {data_sample.length === 0 ? (
            <div className="text-gray-600 text-center py-8 text-sm">No data available</div>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500 uppercase tracking-wide">
                  {Object.keys(data_sample[0]).map((key) => (
                    <th key={key} className="text-left px-3 py-2 whitespace-nowrap">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data_sample.map((row, i) => (
                  <tr key={i} className="border-b border-gray-800/50">
                    {Object.values(row).map((val, j) => (
                      <td key={j} className="px-3 py-1.5 text-gray-400 whitespace-nowrap max-w-[200px] truncate">
                        {val === null ? (
                          <span className="text-red-400/60 italic">null</span>
                        ) : (
                          String(val)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
