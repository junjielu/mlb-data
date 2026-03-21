# AGENTS Guide

## 项目目标
- 本项目用于从 Fangraphs 拉取 MLB depth charts 与 current injury report 数据，并发布为前端可消费的静态快照。
- 默认前端读取入口是 `public/data/latest/` 下的浏览器消费型产物，其中核心是 `depth-charts.json`，伤病数据是独立的 `injuries.json`；不要再把 QA 文件当作公共输出的一部分。
- 如果没有用户明确说明，不再以 Notion 作为标准输出目标。
- 当前线上发布目标是 Vercel；静态站点目录为 `public/`，SPA 路由重写由 `vercel.json` 管理。

## 默认工作边界（必须遵守）
- 未经明确指令，不要修改赛季参数；depth charts 主数据流默认维护 `2025`。
- 未经明确指令，不要变更公开快照 schema 的主版本号。
- 未经明确指令，不要把 operator/QA 产物重新暴露到前端公共读取面。
- `data/builds/depth-charts/candidates/` 是 depth charts 的内部候选构建区；这里允许生成 `quality-report.json`、`review-status.json` 等门禁产物。
- `public/data/latest/` 只应承载浏览器消费型发布产物；前端当前实际消费的是 `depth-charts.json` 与 `injuries.json`。
- `public/data/backups/` 仅用于回滚或保留历史发布，不作为前端读取入口。
- `data/notion_*` 属于历史遗留输入/产物；无明确需求时不再参与主流程。

## 当前目录约定

### 1) Fangraphs 原始抓取输出
- `data/fangraphs_batter_2025.json`
- `data/fangraphs_sp_2025.json`
- `data/fangraphs_rp_2025.json`
- `data/fangraphs_injuries_current.json`

### 2) Depth Charts 内部构建与审核区
- `data/builds/depth-charts/candidates/<build_id>/depth-charts.json`
- `data/builds/depth-charts/candidates/<build_id>/quality-report.json`
- `data/builds/depth-charts/candidates/<build_id>/review-status.json`

说明：
- 这些文件属于内部候选与审核面，不是公共前端契约。
- `quality-report.json` 与 `review-status.json` 当前由 QA/审核脚本使用。

### 3) 公共发布面
- `public/data/latest/depth-charts.json`
- `public/data/latest/injuries.json`

说明：
- `depth-charts.json` 是清洗后的公开快照，发布时会去掉 operator 诊断字段。
- `injuries.json` 是独立发布的 current injury artifact，不与 2025 depth charts 绑定版本推进。
- `quality-report.json` 与 `review-status.json` 不应继续保留在 `public/data/latest/`。

## 核心脚本与职责

### 1) 数据抓取层
- `scripts/fangraphs_batter_sync.py`
- `scripts/fangraphs_sp_sync.py`
- `scripts/fangraphs_rp_sync.py`
- `scripts/fangraphs_injury_sync.py`

职责：
- 从 Fangraphs 获取 Batter/SP/RP 原始结构化数据，输出到 `data/fangraphs_*_2025.json`。
- 从 Fangraphs 获取 current injury report，输出到 `data/fangraphs_injuries_current.json`。

### 2) Depth Charts 聚合、门禁与发布层
- `scripts/depth_charts_pipeline.py`

职责：
- 聚合 Batter/SP/RP 三份抓取数据为统一候选快照。
- 生成内部 `quality-report.json` 与 `review-status.json`。
- 执行结构检查、missing-data 分类、回归检查与发布门禁。
- 在门禁通过或 review 批准后，原子发布清洗后的 `public/data/latest/depth-charts.json`。
- 支持基于 `public/data/backups/` 的发布回滚。

子命令约定：
- `build`：生成候选构建，可选直接发布。
- `review`：对需要人工确认的候选 build 做批准。
- `publish`：发布指定候选 build。
- `rollback`：从备份恢复 `latest`。

### 3) Injury Report 发布层
- `scripts/injury_report_pipeline.py`

职责：
- 验证 `data/fangraphs_injuries_current.json`。
- 独立发布 `public/data/latest/injuries.json`。
- 在刷新失败时保留上一版 injury latest，不覆盖已有公共产物。

### 4) 质量验证层
- `scripts/regression_checks.py`
- `scripts/qa_go_no_go.py`

职责：
- 验证关键回归行，如 `NYY SU7`、`TOR SU7`、`LAD`/`ATH`/`WSN` 指定球员匹配。
- 基于内部候选产物生成 go/no-go 报告。

注意：
- 这两个脚本默认读取 `data/builds/depth-charts/` 下最新 candidate。
- 如果没有 candidate，它们才会回退读取 `public/data/latest/`。

### 5) 前端展示层
- `public/index.html`
- `public/app.js`
- `public/styles.css`
- `scripts/serve_web.py`
- `vercel.json`

职责：
- 提供 `/teams` 与 `/team/:abbr` 页面。
- team detail 页按固定顺序展示 Batter、SP、RP、Current Injury Report。
- 前端从 `depth-charts.json` 与 `injuries.json` 分别加载 2025 depth charts 和 current injury 数据。
- 前端必须区分“某队当前没有 injury entries”和“injury 数据暂时不可用”。
- 确保 SPA 路由在本地和部署环境下都可刷新访问。

## 标准执行流程（建议）
1. 运行抓取脚本更新 `data/fangraphs_batter_2025.json`、`data/fangraphs_sp_2025.json`、`data/fangraphs_rp_2025.json`。
2. 运行 `python3 scripts/depth_charts_pipeline.py build --season 2025` 生成 candidate。
3. 运行 `python3 scripts/regression_checks.py`。
4. 运行 `python3 scripts/qa_go_no_go.py` 并检查报告。
5. 如果 build 需要人工 review，运行 `python3 scripts/depth_charts_pipeline.py review --build-id <build_id> --reviewer <name> --note "<note>"`。
6. 运行 `python3 scripts/depth_charts_pipeline.py publish --build-id <build_id>` 发布到 `public/data/latest/depth-charts.json`。
7. 如需刷新伤病数据，运行 `python3 scripts/fangraphs_injury_sync.py`，然后运行 `python3 scripts/injury_report_pipeline.py refresh`。
8. 通过 `python3 scripts/serve_web.py` 本地验证 `/teams` 与 `/team/:abbr`。
9. 发布到 Vercel：`vercel --prod`。

补充：
- 若确定候选 build 无需额外 review，也可直接使用 `python3 scripts/depth_charts_pipeline.py build --season 2025 --publish`。
- injury 数据刷新与 depth charts 发布相互独立，不要求同一次执行完成。

## 变更规则
- 改动公开 schema、门禁阈值、核心匹配逻辑、公共发布边界或 injury/depth-charts 数据契约时，必须同步更新 OpenSpec 与运行文档。
- 仅在用户明确要求时，才恢复或新增 Notion 同步相关流程。
- 已归档的历史 change 仅作背景参考；新增需求请走新的 OpenSpec change。
