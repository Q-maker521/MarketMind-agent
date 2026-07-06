# 验收清单

在推送到 GitHub、部署线上环境或用于面试展示前，可以按这份清单做一次完整验收。

## 本地服务

- [ ] 后端可以启动在 `http://127.0.0.1:8000`
- [ ] 前端可以启动在 `http://127.0.0.1:5173`
- [ ] `GET /health` 返回 `{"status":"ok"}`
- [ ] `GET /api/system/capabilities` 返回运行时元数据
- [ ] 前端系统能力面板可以运行 provider 诊断

## 前端工作流

- [ ] Demo 模式可以创建并加载稳定的样例报告
- [ ] Workflow 模式可以运行一个新的 LangGraph 任务
- [ ] 报告页签展示摘要、Markdown 报告和质量评审结果
- [ ] 链路页签展示工作流节点和执行耗时
- [ ] 工具调用页签展示工具名称、状态、输入、输出和耗时
- [ ] 失败的工具调用有明显的视觉区分
- [ ] provider 失败时出现 fallback 提示
- [ ] provider 诊断展示行情 provider 和 LLM provider 的状态、延迟和错误详情

## 任务历史

- [ ] 最近任务出现在左侧历史面板
- [ ] 点击历史任务可以恢复报告、链路、工具调用和评审结果
- [ ] 股票代码筛选可用
- [ ] 运行模式筛选可用
- [ ] 状态筛选可用
- [ ] 刷新按钮可以重新加载历史
- [ ] 历史卡片展示运行模式、质量分、fallback 状态、行情 provider 和 LLM provider

## 后端 API

- [ ] `POST /api/analysis-tasks`
- [ ] `POST /api/analysis-tasks/workflow`
- [ ] `POST /api/system/provider-diagnostics`
- [ ] `GET /api/analysis-tasks`
- [ ] `GET /api/analysis-tasks/{task_id}`
- [ ] `GET /api/analysis-tasks/{task_id}/steps`
- [ ] `GET /api/analysis-tasks/{task_id}/tool-calls`
- [ ] `GET /api/analysis-tasks/{task_id}/report`

## 验证命令

```bash
python -m compileall backend\app
cd frontend
npm run build
```

## GitHub 提交卫生

- [ ] `backend/marketmind.db` 没有被提交
- [ ] `backend/server.log` 和 `backend/server.err.log` 没有被提交
- [ ] `frontend/node_modules` 没有被提交
- [ ] `frontend/dist` 没有被提交
- [ ] 真实 `.env` 文件没有被提交
- [ ] `.env.example` 文件已经被提交

## 演示脚本

1. 打开前端页面。
2. 指出系统能力面板。
3. 运行 provider 诊断，并解释真实/模拟 provider 的可观测性。
4. 使用 `AAPL` 运行 Workflow 模式。
5. 打开链路页签，解释每个 Agent 节点。
6. 打开工具调用页签，解释 provider/tool 的可观测性。
7. 打开报告页签，解释质量评审。
8. 使用历史筛选功能重新加载之前的工作流任务。
