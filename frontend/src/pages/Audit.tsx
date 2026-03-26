import AuditLogTable from "../components/AuditLogTable";

export default function Audit() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white">Audit Log</h1>
      <p className="text-sm text-gray-500">
        Full history of all autonomous agent decisions
      </p>
      <AuditLogTable />
    </div>
  );
}
