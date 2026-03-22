## Why

The current Batter experience makes platoon comparison harder than it needs to be because users can inspect only one lineup view at a time, even though the product value comes from comparing `vsR` and `vsL` side by side. Fangraphs platoon lineup pages also publish handedness-specific `Bench` rows, so the public snapshot should preserve that source information instead of limiting the public contract to the nine projected starters.

## What Changes

- **BREAKING** Extend the public batter release contract in `depth-charts.json` so each team publishes handedness-specific `alternates` collections alongside the existing `vsR` and `vsL` starter lineups.
- Update the Fangraphs batter ingest and publish pipeline to preserve handedness-specific `Bench` rows from RosterResource platoon pages while excluding non-bench statuses such as projected injured-list rows from the new public alternates contract.
- Preserve the existing consumer-facing batter row metrics, identity fields, age, recent history, and platoon role labeling for both starter and alternate batter rows.
- Update the team detail Batter section to present `vs RHP` and `vs LHP` simultaneously, showing each handedness's starting lineup together with its corresponding primary alternates rather than forcing a toggle between views.
- Extend structural validation and regression coverage so publish gating understands the new alternates collections without regressing the existing batter baseline behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: Public batter publication changes from dual starter lineups only to dual starter lineups plus handedness-specific public alternates derived from Fangraphs `Bench` rows.
- `depth-charts-web-ui`: The team detail Batter section changes from a switchable platoon view to a simultaneous side-by-side platoon comparison that shows both starter lineups and their corresponding primary alternates.

## Impact

- Affected data ingest and publish scripts: [`scripts/fangraphs_batter_sync.py`](/Users/ballad/Documents/Tools/notion/scripts/fangraphs_batter_sync.py), [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py), [`scripts/regression_checks.py`](/Users/ballad/Documents/Tools/notion/scripts/regression_checks.py), [`scripts/qa_go_no_go.py`](/Users/ballad/Documents/Tools/notion/scripts/qa_go_no_go.py)
- Affected public artifact contract: [`public/data/latest/depth-charts.json`](/Users/ballad/Documents/Tools/notion/public/data/latest/depth-charts.json)
- Affected frontend surface: [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js), [`public/styles.css`](/Users/ballad/Documents/Tools/notion/public/styles.css), and the Batter section layout on `/team/:abbr`
- External dependency: Fangraphs RosterResource `platoon-lineups/<team>` pages and their handedness-specific `Bench` rows
