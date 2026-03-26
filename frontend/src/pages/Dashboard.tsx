import { useApi } from "../hooks/useApi";
import { useSSE } from "../hooks/useSSE";
import type { Pipeline } from "../types";
import StatsBar from "../components/StatsBar";
import PipelineGrid from "../components/PipelineGrid";
import LiveAlertFeed from "../components/LiveAlertFeed";

const demoPipelines: Pipeline[] = [
  { id: "1", dag_id: "etl_user_events", name: "User Events ETL", description: "Ingests user clickstream events", schedule: "*/15 * * * *", source_type: "Kafka", status: "warning", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 2, last_run_time: new Date(Date.now() - 900000).toISOString() },
  { id: "2", dag_id: "etl_transactions", name: "Transaction Processing", description: "Processes financial transactions", schedule: "*/5 * * * *", source_type: "PostgreSQL", status: "healthy", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 0, last_run_time: new Date(Date.now() - 300000).toISOString() },
  { id: "3", dag_id: "etl_inventory_sync", name: "Inventory Sync", description: "Synchronizes product inventory", schedule: "0 * * * *", source_type: "REST API", status: "warning", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 1, last_run_time: new Date(Date.now() - 3600000).toISOString() },
  { id: "4", dag_id: "etl_customer_profiles", name: "Customer Profile Enrichment", description: "Enriches customer profiles", schedule: "0 2 * * *", source_type: "S3", status: "critical", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 3, last_run_time: new Date(Date.now() - 7200000).toISOString() },
  { id: "5", dag_id: "etl_log_aggregation", name: "Log Aggregation Pipeline", description: "Aggregates application logs", schedule: "*/10 * * * *", source_type: "Filebeat", status: "healthy", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 0, last_run_time: new Date(Date.now() - 600000).toISOString() },
  { id: "6", dag_id: "etl_marketing_campaigns", name: "Marketing Campaign Analytics", description: "Campaign performance metrics", schedule: "0 6 * * *", source_type: "Google Ads API", status: "warning", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 1, last_run_time: new Date(Date.now() - 21600000).toISOString() },
  { id: "7", dag_id: "etl_sensor_data", name: "IoT Sensor Ingestion", description: "Temperature, humidity, pressure readings", schedule: "*/2 * * * *", source_type: "MQTT", status: "healthy", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 0, last_run_time: new Date(Date.now() - 120000).toISOString() },
  { id: "8", dag_id: "etl_order_fulfillment", name: "Order Fulfillment Tracker", description: "Tracks order status updates", schedule: "*/30 * * * *", source_type: "Webhook", status: "warning", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 1, last_run_time: new Date(Date.now() - 1800000).toISOString() },
  { id: "9", dag_id: "etl_product_reviews", name: "Product Review Aggregator", description: "Collects product reviews", schedule: "0 4 * * *", source_type: "Web Scraper", status: "healthy", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 0, last_run_time: new Date(Date.now() - 14400000).toISOString() },
  { id: "10", dag_id: "etl_fraud_detection", name: "Fraud Detection Features", description: "Real-time fraud detection features", schedule: "*/5 * * * *", source_type: "Kafka", status: "critical", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 2, last_run_time: new Date(Date.now() - 300000).toISOString() },
  { id: "11", dag_id: "etl_email_events", name: "Email Event Processing", description: "Email delivery and click events", schedule: "*/15 * * * *", source_type: "SendGrid API", status: "healthy", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 0, last_run_time: new Date(Date.now() - 900000).toISOString() },
  { id: "12", dag_id: "etl_data_warehouse", name: "Data Warehouse Refresh", description: "Full analytics warehouse refresh", schedule: "0 1 * * *", source_type: "Multiple", status: "warning", created_at: new Date().toISOString(), updated_at: new Date().toISOString(), anomaly_count: 1, last_run_time: new Date(Date.now() - 3600000).toISOString() },
];

export default function Dashboard() {
  const { data: pipelines, loading } = useApi<Pipeline[]>("/pipelines");
  const alerts = useSSE();

  const displayPipelines = pipelines && pipelines.length > 0 ? pipelines : demoPipelines;

  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 space-y-6 min-w-0">
        <StatsBar />
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Pipeline Health</h2>
          {loading ? (
            <div className="text-gray-600 text-center py-12">Loading pipelines...</div>
          ) : (
            <PipelineGrid pipelines={displayPipelines} />
          )}
        </div>
      </div>
      <div className="w-80 flex-shrink-0">
        <LiveAlertFeed alerts={alerts} />
      </div>
    </div>
  );
}
