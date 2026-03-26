import { useApi } from "../hooks/useApi";
import { useSSE } from "../hooks/useSSE";
import type { Pipeline } from "../types";
import StatsBar from "../components/StatsBar";
import PipelineGrid from "../components/PipelineGrid";
import LiveAlertFeed from "../components/LiveAlertFeed";

export default function Dashboard() {
  const { data: pipelines, loading } = useApi<Pipeline[]>("/pipelines");
  const alerts = useSSE();

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 space-y-6 min-w-0">
        <StatsBar />
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Pipeline Health</h2>
          {loading ? (
            <div className="text-gray-600 text-center py-12">Loading pipelines...</div>
          ) : (
            <PipelineGrid pipelines={pipelines || []} />
          )}
        </div>
      </div>
      <div className="w-80 flex-shrink-0">
        <LiveAlertFeed alerts={alerts} />
      </div>
    </div>
  );
}
