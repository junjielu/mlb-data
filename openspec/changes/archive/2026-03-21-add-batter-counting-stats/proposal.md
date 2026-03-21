## Why

The public batter table currently exposes only `wRC+`, `AVG`, `OBP`, and `SLG`, even though the Fangraphs batting source already returns common counting stats such as `R`, `HR`, `RBI`, and `SB`. This makes the team detail page less useful for quick lineup scanning and hides source data that is already available through the existing ingest path.

## What Changes

- Extend batter rows in the published depth chart snapshot to retain Fangraphs `R`, `HR`, `RBI`, and `SB` values alongside the existing batting metrics.
- Update the team detail Batter table to display `R`, `HR`, `RBI`, and `SB` immediately after `Position`, with `wRC+` moved to the final Batter column.
- Preserve the current consumer-facing behavior for missing values by continuing to render `--` when any newly added counting stat is absent.
- Keep operator-only diagnostics out of the public artifact and avoid coupling this UI enhancement to injury data or other sections.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `depth-charts-data-pipeline`: The published batter row contract changes to include Fangraphs counting stats `R`, `HR`, `RBI`, and `SB` in public release artifacts.
- `depth-charts-web-ui`: The team detail Batter table changes to render the new counting stat columns after `Position` and move `wRC+` to the final column.

## Impact

- Affected ingest and publish code: `scripts/fangraphs_batter_sync.py`, `scripts/depth_charts_pipeline.py`
- Affected frontend code: `public/app.js`, and potentially `public/styles.css` if table spacing needs adjustment
- Affected public artifact contract: `public/data/latest/depth-charts.json`
- Affected documentation/spec artifacts for the depth charts pipeline and web UI
