## Context

当前的 depth charts 数据流会从 Fangraphs 抓取 Batter、SP、RP 行数据，经过 `scripts/depth_charts_pipeline.py` 聚合后发布到公开快照 `public/data/latest/depth-charts.json`，再由 [public/app.js](/Users/ballad/Documents/Tools/notion/public/app.js) 渲染 `/team/:abbr` 页面。现有公开行数据已经包含姓名、角色、位置、链接和各类消费型指标，但没有年龄字段，因此前端无法在姓名右侧直接显示年龄。

这次变更跨越抓取脚本、聚合发布脚本和前端展示层，属于一个小范围但跨模块的数据契约扩展。项目约束要求保持 `2025` 赛季参数不变、公开 schema 主版本不变、并继续隔离 operator-only 诊断字段，因此年龄需要作为消费型字段进入现有发布面，而不是通过 QA 或内部 candidate 补充。

## Goals / Non-Goals

**Goals:**
- 从 Fangraphs 原始 Batter、SP、RP 数据中提取每个球员的年龄。
- 在公开 `depth-charts.json` 的 Batter、SP、RP 主行中稳定发布年龄字段，供前端直接消费。
- 在 team detail 页面把年龄显示在姓名右侧，且不破坏现有链接、排序、展开历史和缺失值渲染。

**Non-Goals:**
- 不调整 injury 数据流或 injury 页面展示。
- 不新增独立的年龄筛选、排序或分组能力。
- 不为 2024/2023 历史行补充年龄，除非实现中 Fangraphs 历史接口已经天然提供且无需额外契约变更。
- 不修改公开 schema 主版本或恢复 Notion 输出流程。

## Decisions

### 1. 年龄以字符串形式进入公开主行数据

公开快照中的年龄字段应沿用现有消费型字段风格，以轻量、直接可渲染的字符串值发布在 Batter、SP、RP 主行上。这样可以避免前端二次格式化，也能与当前 `safeMetric()` 的缺失值渲染逻辑兼容。

备选方案是发布数字类型并让前端格式化，但当前快照中的大多数展示指标已经是字符串形式，单独为年龄引入不同类型不会带来明显收益，反而增加前端分支处理。

### 2. 年龄在抓取阶段提取，在聚合阶段透传到公开发布面

年龄最合适的来源是 Fangraphs 当前 depth chart / leaders 响应中的球员行字段，因此应该在 `fangraphs_batter_sync.py`、`fangraphs_sp_sync.py`、`fangraphs_rp_sync.py` 生成原始结构化文件时就保留下来，再由 `depth_charts_pipeline.py` 在 sanitize/publish 过程中透传。

备选方案是在前端根据生日或额外接口临时计算年龄，但当前前端没有生日数据，也不应为展示一个简单字段新增运行时远程依赖。

### 3. 前端把年龄作为姓名的附属标签，而不是新增独立列

用户需求明确要求“在名字右侧加上年龄”，因此 UI 应在现有姓名单元格内把年龄渲染成附属文本，例如 `Name · 27` 或类似轻量样式，而不是新增独立 `Age` 列。这样可以保持现有表宽和比较模型稳定，尤其对 Batter/SP/RP 不同表结构都更一致。

备选方案是新增列，但这会扩大列宽、影响移动端可读性，也偏离用户给出的展示位置要求。

### 4. 年龄缺失时保持静默降级

如果 Fangraphs 对个别球员没有可解析年龄，公开快照可以把年龄字段留空，前端在姓名右侧不渲染年龄标签。这样能复用现有“缺失值不阻断发布”的原则，避免为了非关键展示字段把 candidate 锁死在 review 或 blocking 状态。

备选方案是在前端显示 `--` 或 `Age unavailable`，但在姓名旁插入缺失占位会降低可读性，也没有当前需求价值。

## Risks / Trade-offs

- [抓取源字段名称不一致] → Batter 与 Pitching 源数据里的年龄字段命名可能不同，需要在实现时先核对真实响应字段并为三条抓取链路分别适配。
- [公开契约扩展带来前后端耦合] → 通过 OpenSpec delta spec 明确年龄是公开消费型字段，并限定在主行范围内，避免后续实现出现历史行或内部字段混用。
- [姓名单元格增加信息影响移动端布局] → 使用附属小号文本样式，并保持年龄简短显示，避免新增独立列导致表格进一步横向膨胀。
- [个别球员年龄缺失] → 允许发布时留空，前端静默隐藏年龄标签，不把该字段纳入 publish blocking 条件。

## Migration Plan

1. 更新 Fangraphs Batter/SP/RP 抓取脚本，确认并保留年龄字段。
2. 更新 `depth_charts_pipeline.py` 的公开行组装与 sanitize 逻辑，把年龄透传到发布快照。
3. 更新前端姓名单元格渲染和样式，在主行姓名右侧显示年龄。
4. 重新生成 candidate，验证 QA/回归不因年龄字段扩展而受阻。
5. 发布新的 `public/data/latest/depth-charts.json`，本地预览确认 `/team/:abbr` 页面展示。

回滚方式维持现有 `public/data/backups/` 发布机制；如果前端展示或契约扩展出现问题，可直接回滚到上一版 `depth-charts.json`。

## Open Questions

- 无阻塞性开放问题；实现时只需确认三条 Fangraphs 抓取链路中年龄字段的真实键名和格式。
