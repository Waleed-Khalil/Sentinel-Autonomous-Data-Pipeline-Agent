import { Link } from "react-router-dom";

const anomalyTypes = [
  {
    name: "Schema Drift",
    color: "border-purple-500/40 bg-purple-950/20",
    icon: (
      <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25a2.25 2.25 0 0 1-2.25-2.25v-2.25Z" />
      </svg>
    ),
    description: "Detects when the structure of incoming data changes unexpectedly.",
    details: [
      "New columns added to incoming records",
      "Expected columns missing from data",
      "Column data types changed (e.g. number became string)",
    ],
  },
  {
    name: "Null Spikes",
    color: "border-yellow-500/40 bg-yellow-950/20",
    icon: (
      <svg className="w-6 h-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
      </svg>
    ),
    description: "Identifies when null/missing values in a column exceed a safe threshold.",
    details: [
      "Configurable threshold (default: 15% null rate)",
      "Tracks null counts per column per run",
      "Severity escalates: warning at 15%, critical at 50%",
    ],
  },
  {
    name: "Statistical Anomalies",
    color: "border-cyan-500/40 bg-cyan-950/20",
    icon: (
      <svg className="w-6 h-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
      </svg>
    ),
    description: "Flags numeric values that fall outside the expected statistical range.",
    details: [
      "Establishes baseline from previous run (mean and std dev)",
      "Flags values beyond 3 standard deviations",
      "Alerts when >10% of values are outliers",
    ],
  },
];

const healingActions = [
  {
    action: "Skip Bad Records",
    code: "skip_bad_records",
    description: "Removes or skips individual records containing anomalous data. Best for isolated bad records that represent a small percentage of the batch.",
    color: "text-orange-400",
  },
  {
    action: "Apply Defaults",
    code: "apply_defaults",
    description: "Replaces null or missing values with computed defaults (mean for numbers, \"N/A\" for strings). Keeps the pipeline flowing when data is expected to exist.",
    color: "text-blue-400",
  },
  {
    action: "Trigger DAG Retry",
    code: "trigger_dag_retry",
    description: "Re-runs the entire DAG from scratch. Best for transient upstream failures that may have already been resolved.",
    color: "text-green-400",
  },
  {
    action: "Quarantine Records",
    code: "quarantine_records",
    description: "Isolates all records from the anomalous run into quarantine for manual review. Used for critical issues like schema changes or large-scale data corruption.",
    color: "text-red-400",
  },
];

const architectureSteps = [
  {
    step: "1",
    title: "Continuous Monitoring",
    description: "A background scanner runs every 60 seconds, iterating over all registered DAGs and their latest run data.",
  },
  {
    step: "2",
    title: "Anomaly Detection",
    description: "Each DAG's latest data is compared against previous runs. The detector checks for schema drift, null spikes, and statistical outliers simultaneously.",
  },
  {
    step: "3",
    title: "Claude Analysis",
    description: "Detected anomalies are sent to Claude with full context: DAG name, anomaly type, severity, and detailed metrics. Claude reasons about the best remediation strategy.",
  },
  {
    step: "4",
    title: "Autonomous Remediation",
    description: "Claude's recommended action is executed automatically: skipping records, applying defaults, retrying the DAG, or quarantining data.",
  },
  {
    step: "5",
    title: "Audit & Observe",
    description: "Every decision is logged with Claude's reasoning, the action taken, and the outcome. Live SSE events stream alerts to the dashboard in real time.",
  },
];

export default function HowItWorks() {
  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-12">
      {/* Hero */}
      <div className="text-center space-y-4 pt-4">
        <h1 className="text-3xl font-bold text-white">
          How <span className="text-blue-400">Sentinel</span> Works
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto leading-relaxed">
          Sentinel is an autonomous data pipeline monitoring agent that continuously watches your
          Airflow DAGs, detects data quality anomalies, and uses Claude to reason about and
          apply self-healing actions — all without human intervention.
        </p>
      </div>

      {/* Architecture Flow */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">The Self-Healing Loop</h2>
        <div className="space-y-3">
          {architectureSteps.map((s) => (
            <div key={s.step} className="flex gap-4 items-start bg-gray-900 border border-gray-800 rounded-lg p-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 text-sm font-bold">
                {s.step}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">{s.title}</h3>
                <p className="text-sm text-gray-400 mt-0.5">{s.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* System Diagram */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">System Architecture</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <pre className="text-xs text-gray-400 font-mono leading-relaxed overflow-x-auto">{`
  React Dashboard (Tailwind CSS)          Live SSE Feed
  ┌──────────────────────────────┐      ┌──────────────┐
  │  Pipeline Grid  │  Alerts    │ ◄──  │  Real-time    │
  │  DAG Detail     │  Audit Log │      │  Event Stream │
  └────────┬─────────────────────┘      └──────┬───────┘
           │ REST API                          │
           ▼                                   │
  ┌────────────────────────────────────────────┤
  │              FastAPI Backend                │
  │                                            │
  │  ┌─────────────┐   ┌──────────────────┐   │
  │  │  Anomaly     │──►│  Claude Healer   │   │
  │  │  Detector    │   │  (Anthropic API) │   │
  │  │              │   │                  │   │
  │  │ - Schema     │   │ - Analyzes context│  │
  │  │ - Nulls      │   │ - Picks action   │   │
  │  │ - Statistics  │   │ - Applies fix    │   │
  │  └──────┬───────┘   └────────┬─────────┘  │
  │         │                    │             │
  └─────────┼────────────────────┼─────────────┘
            │                    │
            ▼                    ▼
  ┌──────────────────────────────────────────┐
  │              PostgreSQL                   │
  │                                          │
  │  dags │ dag_runs │ pipeline_data         │
  │  anomalies │ audit_log                   │
  └──────────────────────────────────────────┘`}
          </pre>
        </div>
      </section>

      {/* Anomaly Types */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Anomaly Detection</h2>
        <p className="text-sm text-gray-400">
          Sentinel detects three categories of data quality issues by comparing each DAG's latest run against its historical baseline.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {anomalyTypes.map((type) => (
            <div key={type.name} className={`border rounded-lg p-4 space-y-3 ${type.color}`}>
              <div className="flex items-center gap-2">
                {type.icon}
                <h3 className="font-semibold text-white">{type.name}</h3>
              </div>
              <p className="text-sm text-gray-400">{type.description}</p>
              <ul className="space-y-1">
                {type.details.map((d, i) => (
                  <li key={i} className="text-xs text-gray-500 flex items-start gap-1.5">
                    <span className="text-gray-600 mt-0.5">-</span>
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Healing Actions */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Self-Healing Actions</h2>
        <p className="text-sm text-gray-400">
          When an anomaly is detected, Claude analyzes the failure context and selects the most
          appropriate remediation. Each action is applied automatically and logged for audit.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {healingActions.map((ha) => (
            <div key={ha.code} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-sm font-semibold ${ha.color}`}>{ha.action}</span>
                <code className="text-[10px] bg-gray-800 text-gray-500 px-1.5 py-0.5 rounded">
                  {ha.code}
                </code>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">{ha.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Claude's Role */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">How Claude Decides</h2>
        <div className="bg-blue-950/20 border border-blue-500/20 rounded-lg p-5 space-y-3">
          <p className="text-sm text-gray-300 leading-relaxed">
            Each anomaly is sent to Claude with full context: the DAG identifier, anomaly type
            and severity, a description of what was detected, and detailed metrics (null percentages,
            z-scores, column names, etc).
          </p>
          <p className="text-sm text-gray-300 leading-relaxed">
            Claude evaluates the severity, considers the type of data involved, and weighs the
            trade-offs between different remediation strategies. It returns a structured decision
            with the chosen action, a confidence score, and a natural language explanation of its
            reasoning.
          </p>
          <p className="text-sm text-gray-300 leading-relaxed">
            If the Claude API is unavailable, Sentinel falls back to a deterministic rule-based
            engine that selects actions based on anomaly type and severity thresholds — ensuring
            the pipeline never stops healing.
          </p>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Tech Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { name: "Python", role: "Backend" },
            { name: "FastAPI", role: "API Server" },
            { name: "Claude API", role: "AI Reasoning" },
            { name: "PostgreSQL", role: "Database" },
            { name: "React", role: "Frontend" },
            { name: "TypeScript", role: "Type Safety" },
            { name: "Tailwind CSS", role: "Styling" },
            { name: "Docker", role: "Infrastructure" },
          ].map((tech) => (
            <div key={tech.name} className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-2.5 text-center">
              <div className="text-sm font-medium text-white">{tech.name}</div>
              <div className="text-[10px] text-gray-500 mt-0.5">{tech.role}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Try It */}
      <section className="bg-gray-900 border border-gray-800 rounded-lg p-6 text-center space-y-3">
        <h2 className="text-lg font-semibold text-white">Try It Out</h2>
        <p className="text-sm text-gray-400 max-w-lg mx-auto">
          Head to the dashboard, click any DAG marked as "warning" or "critical",
          and hit <strong className="text-white">Trigger Scan</strong> to watch Sentinel detect
          anomalies and resolve them autonomously in real time.
        </p>
        <Link
          to="/"
          className="inline-block bg-blue-600 hover:bg-blue-500 text-white text-sm px-5 py-2 rounded-lg transition mt-2"
        >
          Go to Dashboard
        </Link>
      </section>
    </div>
  );
}
