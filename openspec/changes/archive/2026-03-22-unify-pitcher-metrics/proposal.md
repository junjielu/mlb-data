## Why

The current public depth chart experience presents SP and RP with different metric sets, which makes pitcher sections harder to compare and forces users to relearn the table model when moving between starters and relievers. At the same time, the published pitcher contract omits metrics the product now wants to surface, so the data pipeline and web UI need to converge on a single public pitcher shape.

## What Changes

- **BREAKING** Remove `k_pct` from the public RP release contract and from the RP web table.
- **BREAKING** Standardize both public SP and RP rows, including recent history entries, on the metric order `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, `BABIP`.
- Extend SP and RP ingestion so the public depth chart snapshot publishes `whip`, `location_plus`, `vfa`, and `babip` for relievers and publishes `vfa` and `babip` for starters.
- Update the public team detail UI so SP and RP render with the same ordered pitcher columns and display `vFA` and `BABIP` immediately after `Location+`.
- Preserve existing missing-value treatment so newly added pitcher metrics render as `--` when Fangraphs does not provide a usable value.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: Change the published SP and RP metric contract so both sections expose the same public pitcher metrics, remove RP `k_pct`, and include `vfa` and `babip` in primary and history rows.
- `depth-charts-web-ui`: Change the SP and RP table presentation so both sections render the same ordered pitcher columns and show `vFA` and `BABIP` after `Location+`.

## Impact

- Affected code: `scripts/fangraphs_sp_sync.py`, `scripts/fangraphs_rp_sync.py`, `scripts/depth_charts_pipeline.py`, `public/app.js`, and any UI styles tied to pitcher table width or column layout.
- Public artifact impact: `public/data/latest/depth-charts.json` pitcher row shape changes for RP and expands for both SP and RP.
- Validation impact: regression and publish checks may need updates if they assume the old RP metric set or old pitcher row schema.
