# AGENTS Guide

## 项目目标
- 本项目用于从 Fangraphs 拉取 MLB depth charts 数据，并发布为前端可消费的快照。
- 默认交付面：`public/data/latest/depth-charts.json` 与 `public/data/latest/quality-report.json`。
- 如果没有用户明确说明，不再以 Notion 作为标准输出目标。

## 默认工作边界（必须遵守）
- 未经明确指令，不要修改赛季参数（默认维护 `2025` 数据流）。
- 未经明确指令，不要变更快照 schema 的主版本号。
- 允许在 `public/data/candidates/` 生成中间构建产物，但仅在门禁通过后发布到 `public/data/latest/`。

## 核心脚本与职责

### 1) 数据抓取层
- `scripts/fangraphs_batter_sync.py`
- `scripts/fangraphs_sp_sync.py`
- `scripts/fangraphs_rp_sync.py`

职责：从 Fangraphs 获取 Batter/SP/RP 原始结构化数据，输出到 `data/fangraphs_*_2025.json`。

### 2) 聚合与发布层
- `scripts/depth_charts_pipeline.py`

职责：
- 聚合三份抓取数据为统一快照。
- 生成 `quality-report.json`。
- 执行发布门禁。
- 原子发布到 `public/data/latest/`。
- 支持回滚到 `public/data/backups/` 的历史快照。

### 3) 质量验证层
- `scripts/regression_checks.py`
- `scripts/qa_go_no_go.py`

职责：
- 验证关键回归行（如 NYY SU7、TOR SU7）。
- 生成 go/no-go 报告。

### 4) 前端展示层
- `public/index.html`
- `public/app.js`
- `public/styles.css`
- `scripts/serve_web.py`

职责：
- 提供 `/teams`、`/team/:abbr`、`/about-data` 页面。
- 显示状态、告警与数据时间戳。

## 标准执行流程（建议）
1. 运行抓取脚本更新 `data/fangraphs_*_2025.json`。
2. 运行 `python3 scripts/depth_charts_pipeline.py build --season 2025 --publish`。
3. 运行 `python3 scripts/regression_checks.py`。
4. 运行 `python3 scripts/qa_go_no_go.py` 并检查报告。
5. 通过 `python3 scripts/serve_web.py` 本地验证展示。

## 变更规则
- 改动 schema、门禁阈值、或核心匹配逻辑时，必须同步更新 OpenSpec 与运行文档。
- 仅在用户明确要求时，才恢复或新增 Notion 同步相关流程。
