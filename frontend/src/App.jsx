import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  CircleAlert,
  Database,
  FileText,
  Gauge,
  KeyRound,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { marked } from "marked";

import {
  createAnalysisTask,
  createWorkflowAnalysisTask,
  getReport,
  getSteps,
  getSystemCapabilities,
  getTask,
  getTasks,
  getToolCalls,
  runProviderDiagnostics,
} from "./api/client";

const defaultPayload = {
  symbol: "AAPL",
  market: "US",
  time_range: "6mo",
  question: "分析 AAPL 最近 6 个月走势，并总结未来一个月的主要风险。",
};

const statusLabels = {
  READY: "待分析",
  PENDING: "排队中",
  RUNNING: "分析中",
  SUCCESS: "已完成",
  FAILED: "失败",
  CANCELED: "已取消",
};

const stanceLabels = {
  bullish: "偏积极",
  neutral: "中性",
  bearish: "偏谨慎",
};

const runModeCopy = {
  demo: {
    label: "样例演示",
    badge: "公开演示模式",
    action: "运行样例分析",
    loading: "正在载入样例",
    note: "使用固定样例报告，不收集模型 Key，也不会产生真实调用费用。",
  },
  workflow: {
    label: "工作流验证",
    badge: "LangGraph 验证模式",
    action: "运行工作流验证",
    loading: "正在执行工作流",
    note: "调用 LangGraph mock workflow，验证节点流转、工具记录和 SQLite 持久化。",
  },
};

const runModeLabels = {
  demo: "样例演示",
  workflow: "工作流验证",
};

function App() {
  const [payload, setPayload] = useState(defaultPayload);
  const [runMode, setRunMode] = useState("demo");
  const [task, setTask] = useState(null);
  const [steps, setSteps] = useState([]);
  const [toolCalls, setToolCalls] = useState([]);
  const [report, setReport] = useState(null);
  const [historyTasks, setHistoryTasks] = useState([]);
  const [historyFilters, setHistoryFilters] = useState({ symbol: "", run_mode: "", status: "" });
  const [activeTab, setActiveTab] = useState("report");
  const [error, setError] = useState(null);
  const [capabilities, setCapabilities] = useState(null);
  const [capabilitiesError, setCapabilitiesError] = useState(null);
  const [diagnostics, setDiagnostics] = useState(null);
  const [diagnosticsError, setDiagnosticsError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [diagnosticsLoading, setDiagnosticsLoading] = useState(false);

  useEffect(() => {
    loadCapabilities();
    loadHistory();
    runAnalysis();
  }, []);

  async function loadHistory(filters = historyFilters) {
    setHistoryLoading(true);
    try {
      const tasks = await getTasks({ limit: 12, ...filters });
      setHistoryTasks(tasks);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function loadTaskBundle(taskId) {
    const [freshTask, freshSteps, freshToolCalls, freshReport] = await Promise.all([
      getTask(taskId),
      getSteps(taskId),
      getToolCalls(taskId),
      getReport(taskId),
    ]);
    setTask(freshTask);
    setSteps(freshSteps);
    setToolCalls(freshToolCalls);
    setReport(freshReport);
  }

  async function loadCapabilities() {
    try {
      const systemCapabilities = await getSystemCapabilities();
      setCapabilities(systemCapabilities);
      setCapabilitiesError(null);
    } catch (requestError) {
      setCapabilitiesError(requestError.message);
    }
  }

  async function runDiagnostics() {
    setDiagnosticsLoading(true);
    setDiagnosticsError(null);
    try {
      const result = await runProviderDiagnostics({
        symbol: payload.symbol,
        time_range: payload.time_range,
        include_llm: true,
      });
      setDiagnostics(result);
      await loadCapabilities();
    } catch (requestError) {
      setDiagnosticsError(requestError.message);
    } finally {
      setDiagnosticsLoading(false);
    }
  }

  async function runAnalysis(event) {
    event?.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const createTask = runMode === "workflow" ? createWorkflowAnalysisTask : createAnalysisTask;
      const created = await createTask(payload);
      await loadTaskBundle(created.id);
      await loadHistory();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function openHistoryTask(taskId) {
    setLoading(true);
    setError(null);
    try {
      await loadTaskBundle(taskId);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  const mode = runModeCopy[runMode];
  const completedSteps = steps.filter((step) => step.status === "SUCCESS").length;
  const totalDuration = steps.reduce((sum, step) => sum + step.duration_ms, 0);
  const hasProviderFallback = toolCalls.some(
    (call) => call.status === "FAILED" && call.tool_name.endsWith(".get_daily_prices"),
  );
  const reportHtml = useMemo(() => (report ? marked.parse(report.markdown) : ""), [report]);

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="control-panel">
          <div className="brand-lockup">
            <div className="brand-mark">
              <BarChart3 size={22} />
            </div>
            <div>
              <p className="eyebrow">MarketMind Agent</p>
              <h1>可追踪的 AI 投研工作台</h1>
              <p className="brand-subtitle">从问题到报告，每一步都留下证据链。</p>
            </div>
          </div>

          <form className="task-form" onSubmit={runAnalysis}>
            <fieldset className="mode-switch">
              <legend>运行模式</legend>
              <button
                type="button"
                className={runMode === "demo" ? "active" : ""}
                onClick={() => setRunMode("demo")}
              >
                样例演示
              </button>
              <button
                type="button"
                className={runMode === "workflow" ? "active" : ""}
                onClick={() => setRunMode("workflow")}
              >
                工作流验证
              </button>
            </fieldset>

            <label>
              股票代码
              <input
                value={payload.symbol}
                onChange={(event) => setPayload({ ...payload, symbol: event.target.value })}
              />
            </label>

            <div className="form-grid">
              <label>
                市场
                <select
                  value={payload.market}
                  onChange={(event) => setPayload({ ...payload, market: event.target.value })}
                >
                  <option value="US">美股</option>
                </select>
              </label>

              <label>
                时间范围
                <select
                  value={payload.time_range}
                  onChange={(event) => setPayload({ ...payload, time_range: event.target.value })}
                >
                  <option value="1mo">近 1 个月</option>
                  <option value="3mo">近 3 个月</option>
                  <option value="6mo">近 6 个月</option>
                  <option value="1y">近 1 年</option>
                </select>
              </label>
            </div>

            <label>
              研究问题
              <textarea
                value={payload.question}
                onChange={(event) => setPayload({ ...payload, question: event.target.value })}
              />
            </label>

            <button className="primary-action" type="submit" disabled={loading}>
              <Play size={17} />
              {loading ? mode.loading : mode.action}
            </button>
          </form>

          <div className="demo-note">
            <ShieldCheck size={17} />
            <span>{mode.note}</span>
          </div>

          {error ? (
            <div className="error-note">
              <CircleAlert size={17} />
              <span>{error}</span>
            </div>
          ) : null}

          <HistoryPanel
            activeTaskId={task?.id}
            filters={historyFilters}
            historyTasks={historyTasks}
            loading={historyLoading}
            onChangeFilters={setHistoryFilters}
            onRefresh={() => loadHistory()}
            onOpenTask={openHistoryTask}
          />

          <CapabilityPanel
            capabilities={capabilities}
            diagnostics={diagnostics}
            diagnosticsError={diagnosticsError}
            diagnosticsLoading={diagnosticsLoading}
            error={capabilitiesError}
            onRunDiagnostics={runDiagnostics}
          />
        </aside>

        <section className="main-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">
                {payload.symbol.toUpperCase()} / {payload.time_range} / {mode.label}
              </p>
              <h2>投研分析结果</h2>
            </div>
            <div className={runMode === "workflow" ? "demo-badge workflow" : "demo-badge"}>
              <Sparkles size={16} />
              <span>{mode.badge}</span>
            </div>
          </div>

          <header className="status-strip">
            <Metric icon={<Activity size={18} />} label="任务状态" value={statusLabels[task?.status ?? "READY"]} />
            <Metric icon={<Gauge size={18} />} label="节点进度" value={`${completedSteps}/${steps.length || 8}`} />
            <Metric icon={<Database size={18} />} label="链路耗时" value={`${totalDuration || 0} ms`} />
            <Metric icon={<KeyRound size={18} />} label="运行模式" value={mode.label} />
          </header>

          {hasProviderFallback ? (
            <div className="fallback-banner">
              <CircleAlert size={17} />
              <span>真实行情数据源不可用，已降级为本地样例数据。失败原因可在“工具调用”中查看。</span>
            </div>
          ) : null}

          <nav className="tabs" aria-label="结果视图">
            <button className={activeTab === "report" ? "active" : ""} onClick={() => setActiveTab("report")}>
              <FileText size={16} />
              投研报告
            </button>
            <button className={activeTab === "trace" ? "active" : ""} onClick={() => setActiveTab("trace")}>
              <Activity size={16} />
              执行链路
            </button>
            <button className={activeTab === "tools" ? "active" : ""} onClick={() => setActiveTab("tools")}>
              <Database size={16} />
              工具调用
            </button>
          </nav>

          {activeTab === "report" ? <ReportView report={report} reportHtml={reportHtml} /> : null}
          {activeTab === "trace" ? <TraceView steps={steps} /> : null}
          {activeTab === "tools" ? <ToolCallView toolCalls={toolCalls} /> : null}
        </section>
      </section>
    </main>
  );
}

function HistoryPanel({
  activeTaskId,
  filters,
  historyTasks,
  loading,
  onChangeFilters,
  onOpenTask,
  onRefresh,
}) {
  function updateFilter(key, value) {
    onChangeFilters({ ...filters, [key]: value });
  }

  return (
    <section className="history-panel">
      <div className="history-heading">
        <Activity size={17} />
        <h2>历史任务</h2>
        {loading ? <span>刷新中</span> : null}
      </div>
      <div className="history-filters">
        <input
          aria-label="按股票代码筛选"
          placeholder="股票代码"
          value={filters.symbol}
          onChange={(event) => updateFilter("symbol", event.target.value.toUpperCase())}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              onRefresh();
            }
          }}
        />
        <select
          aria-label="按运行模式筛选"
          value={filters.run_mode}
          onChange={(event) => updateFilter("run_mode", event.target.value)}
        >
          <option value="">全部模式</option>
          <option value="demo">样例演示</option>
          <option value="workflow">工作流验证</option>
        </select>
        <select
          aria-label="按状态筛选"
          value={filters.status}
          onChange={(event) => updateFilter("status", event.target.value)}
        >
          <option value="">全部状态</option>
          <option value="SUCCESS">已完成</option>
          <option value="FAILED">失败</option>
          <option value="RUNNING">分析中</option>
        </select>
        <button className="history-refresh" type="button" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={15} />
          刷新
        </button>
      </div>
      {historyTasks.length ? (
        <div className="history-list">
          {historyTasks.map((historyTask) => (
            <button
              type="button"
              className={historyTask.id === activeTaskId ? "history-item active" : "history-item"}
              key={historyTask.id}
              onClick={() => onOpenTask(historyTask.id)}
            >
              <span className="history-symbol">{historyTask.symbol}</span>
              <span className="history-meta">
                {historyTask.time_range} · {runModeLabels[historyTask.run_mode] ?? historyTask.run_mode}
              </span>
              <span className="history-question">{historyTask.question}</span>
              <span className="history-audit">
                <span>{statusLabels[historyTask.status] ?? historyTask.status}</span>
                <span>
                  质量分{" "}
                  {historyTask.quality_score !== null && historyTask.quality_score !== undefined
                    ? `${Math.round(historyTask.quality_score * 100)}%`
                    : "-"}
                </span>
                <span className={historyTask.has_fallback ? "audit-warn" : ""}>
                  {historyTask.has_fallback ? "发生降级" : "无降级"}
                </span>
              </span>
              <span className="history-providers">
                行情 {historyTask.market_data_provider ?? "-"} · 模型 {historyTask.llm_provider ?? "-"}
              </span>
              <span className="history-time">{formatTaskTime(historyTask.created_at)}</span>
            </button>
          ))}
        </div>
      ) : (
        <p className="history-empty">暂无历史任务</p>
      )}
    </section>
  );
}

function formatTaskTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function CapabilityPanel({
  capabilities,
  diagnostics,
  diagnosticsError,
  diagnosticsLoading,
  error,
  onRunDiagnostics,
}) {
  if (error) {
    return (
      <section className="capability-panel">
        <div className="capability-heading">
          <Database size={17} />
          <h2>系统能力</h2>
        </div>
        <p className="capability-error">{error}</p>
      </section>
    );
  }

  if (!capabilities) {
    return (
      <section className="capability-panel">
        <div className="capability-heading">
          <Database size={17} />
          <h2>系统能力</h2>
        </div>
        <p className="capability-muted">正在读取运行配置</p>
      </section>
    );
  }

  const marketDataLabel = capabilities.external_market_data_ready ? "真实行情可用" : "本地样例行情";
  const marketConfigLabel =
    capabilities.configured_market_data_provider === "twelve_data"
      ? "Demo Key"
      : capabilities.alpha_vantage_configured
        ? "已配置"
        : "未配置";
  const llmLabel = capabilities.external_llm_ready ? "真实模型可用" : "本地模板生成";
  const llmKeyLabel = capabilities.llm_api_key_configured ? "已配置" : "未配置";
  const llmModelLabel = capabilities.llm_model ?? "未指定";

  return (
    <section className="capability-panel">
      <div className="capability-heading">
        <Database size={17} />
        <h2>系统能力</h2>
      </div>
      <div className="capability-grid">
        <CapabilityItem label="运行环境" value={capabilities.app_env} />
        <CapabilityItem label="工作流引擎" value={capabilities.workflow_engine} />
        <CapabilityItem label="持久化" value={capabilities.persistence} />
        <CapabilityItem label="行情源" value={marketDataLabel} />
        <CapabilityItem label="实际 Provider" value={capabilities.effective_market_data_provider} />
        <CapabilityItem label="行情配置" value={marketConfigLabel} />
        <CapabilityItem label="模型生成" value={llmLabel} />
        <CapabilityItem label="模型 Provider" value={capabilities.effective_llm_provider} />
        <CapabilityItem label="模型名称" value={llmModelLabel} />
        <CapabilityItem label="LLM Key" value={llmKeyLabel} />
      </div>
      <p className="capability-muted">
        支持市场：{capabilities.supported_markets.join(", ")} · 周期：
        {capabilities.supported_time_ranges.join(", ")}
      </p>
      <button className="diagnostics-action" type="button" onClick={onRunDiagnostics} disabled={diagnosticsLoading}>
        <Activity size={15} />
        {diagnosticsLoading ? "诊断中" : "运行环境诊断"}
      </button>
      {diagnosticsError ? <p className="capability-error">{diagnosticsError}</p> : null}
      {diagnostics ? <DiagnosticsResult diagnostics={diagnostics} /> : null}
    </section>
  );
}

function DiagnosticsResult({ diagnostics }) {
  return (
    <div className="diagnostics-result">
      <DiagnosticCheck title="行情数据源" check={diagnostics.market_data} />
      <DiagnosticCheck title="模型生成源" check={diagnostics.llm} />
    </div>
  );
}

function DiagnosticCheck({ title, check }) {
  const statusText = {
    success: "成功",
    failed: "失败",
    skipped: "跳过",
  }[check.status];

  return (
    <div className={`diagnostic-check ${check.status}`}>
      <div className="diagnostic-heading">
        <strong>{title}</strong>
        <span>{statusText}</span>
      </div>
      <p>{check.summary}</p>
      <dl>
        <div>
          <dt>Provider</dt>
          <dd>{check.provider}</dd>
        </div>
        <div>
          <dt>耗时</dt>
          <dd>{check.latency_ms} ms</dd>
        </div>
      </dl>
      {check.error_message ? <p className="diagnostic-error">{check.error_message}</p> : null}
    </div>
  );
}

function CapabilityItem({ label, value }) {
  return (
    <div className="capability-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <span className="metric-icon">{icon}</span>
      <span className="metric-copy">
        <span>{label}</span>
        <strong>{value}</strong>
      </span>
    </div>
  );
}

function ReportView({ report, reportHtml }) {
  if (!report) {
    return <EmptyState title="暂无报告" body="运行分析后，这里会展示结构化投研报告。" />;
  }

  return (
    <article className="report-layout">
      <div className="report-summary">
        <p className="eyebrow">研究结论</p>
        <h2>{report.title}</h2>
        <p>{report.summary}</p>
        <div className="stance-row">
          <span>{stanceLabels[report.stance] ?? report.stance}</span>
          <span>置信度 {Math.round(report.confidence * 100)}%</span>
          {report.quality_score !== null && report.quality_score !== undefined ? (
            <span>质量分 {Math.round(report.quality_score * 100)}%</span>
          ) : null}
        </div>
        <ReviewChecklist report={report} />
      </div>
      <div className="markdown-body" dangerouslySetInnerHTML={{ __html: reportHtml }} />
    </article>
  );
}

function ReviewChecklist({ report }) {
  if (!report.review_checks?.length) {
    return null;
  }

  return (
    <div className="review-checklist">
      <div className="review-heading">
        <ShieldCheck size={16} />
        <span>{report.review_passed ? "质量检查通过" : "需要人工复核"}</span>
      </div>
      <p>{report.review_summary}</p>
      <ul>
        {report.review_checks.map((check) => (
          <li className={check.passed ? "passed" : "failed"} key={check.id}>
            {check.passed ? <CheckCircle2 size={15} /> : <CircleAlert size={15} />}
            <span>
              <strong>{check.label}</strong>
              {check.detail}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function TraceView({ steps }) {
  if (!steps.length) {
    return <EmptyState title="暂无链路" body="任务载入后，这里会展示每个 Agent 节点的执行摘要。" />;
  }

  return (
    <div className="trace-list">
      {steps.map((step) => (
        <section className="trace-item" key={step.id}>
          <div className="trace-marker">
            <CheckCircle2 size={18} />
          </div>
          <div>
            <div className="trace-heading">
              <h3>{step.title}</h3>
              <span>{step.duration_ms} ms</span>
            </div>
            <p className="node-name">{step.node_name}</p>
            <p>{step.output_summary}</p>
          </div>
        </section>
      ))}
    </div>
  );
}

function ToolCallView({ toolCalls }) {
  if (!toolCalls.length) {
    return <EmptyState title="暂无工具调用" body="任务载入后，这里会展示工具输入、输出和耗时。" />;
  }

  return (
    <div className="tool-grid">
      {toolCalls.map((call) => (
        <section className={`tool-card ${call.status === "FAILED" ? "failed" : ""}`} key={call.id}>
          <div>
            <div className="tool-card-heading">
              <p className="node-name">{call.tool_name}</p>
              <span className={`status-pill ${call.status === "FAILED" ? "failed" : "success"}`}>
                {call.status === "FAILED" ? "失败" : "成功"}
              </span>
            </div>
            <h3>{call.output_summary}</h3>
            {call.error_message ? <p className="tool-error">{call.error_message}</p> : null}
          </div>
          <dl>
            <div>
              <dt>输入</dt>
              <dd>{call.input_summary}</dd>
            </div>
            <div>
              <dt>耗时</dt>
              <dd>{call.duration_ms} ms</dd>
            </div>
          </dl>
        </section>
      ))}
    </div>
  );
}

function EmptyState({ title, body }) {
  return (
    <div className="empty-state">
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}

export default App;
