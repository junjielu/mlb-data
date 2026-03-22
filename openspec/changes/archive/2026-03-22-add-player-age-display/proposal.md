## Why

当前公开 depth charts 数据和前端页面都没有直接展示球员年龄，用户需要跳转到 Fangraphs 或自行推算才能理解打线和轮值的年龄结构。既然现有数据流已经在解析并发布球员基础信息，现在补充年龄字段并在姓名右侧展示，可以让前端消费结果更完整，也避免后续再做额外的客户端推导。

## What Changes

- 在 Fangraphs depth charts 数据解析流程中提取打手和投手年龄，并把年龄纳入公开发布快照。
- 更新公开 `depth-charts.json` 数据契约，让 Batter、SP、RP 行都能向前端提供消费型年龄字段。
- 更新 `/team/:abbr` 页面，在打手和投手姓名右侧显示年龄，同时保持现有表格排序、缺失值处理和链接行为不变。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: 公开发布的 batter、sp、rp 行需要包含从 Fangraphs 解析出的年龄字段，并继续保持公共快照不暴露 operator-only 诊断信息。
- `depth-charts-web-ui`: team detail 页面需要在 Batter、SP、RP 表格中把年龄展示在姓名右侧，并定义年龄缺失时的前端展示行为。

## Impact

- 受影响代码主要包括 Fangraphs 抓取/聚合脚本、`scripts/depth_charts_pipeline.py`、以及 [public/app.js](/Users/ballad/Documents/Tools/notion/public/app.js) 和可能的样式文件。
- 公开发布产物 [public/data/latest/depth-charts.json](/Users/ballad/Documents/Tools/notion/public/data/latest/depth-charts.json) 的行级字段会新增年龄信息。
- 需要同步更新对应 OpenSpec delta specs，确保数据契约和 UI 展示要求一致。
