import { useNavigate } from "react-router-dom";
import type { Pipeline } from "../types";

const statusColors = {
  healthy: "border-green-500/40 bg-green-950/20",
  warning: "border-yellow-500/40 bg-yellow-950/20",
  critical: "border-red-500/40 bg-red-950/20",
};

const statusDots = {
  healthy: "bg-green-400",
  warning: "bg-yellow-400",
  critical: "bg-red-400",
};

function timeAgo(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function PipelineGrid({ pipelines }: { pipelines: Pipeline[] }) {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {pipelines.map((p) => (
        <div
          key={p.dag_id}
          onClick={() => navigate(`/pipeline/${p.dag_id}`)}
          className={`border rounded-lg p-4 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-lg ${statusColors[p.status]}`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className={`w-2.5 h-2.5 rounded-full ${statusDots[p.status]} animate-pulse`} />
              <span className="text-sm font-medium capitalize">{p.status}</span>
            </div>
            {p.anomaly_count > 0 && (
              <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded-full font-medium">
                {p.anomaly_count} alert{p.anomaly_count !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <h3 className="font-semibold text-white mb-1 truncate">{p.name}</h3>
          <p className="text-xs text-gray-500 mb-3 truncate">{p.dag_id}</p>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{p.source_type}</span>
            <span>{timeAgo(p.last_run_time)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
