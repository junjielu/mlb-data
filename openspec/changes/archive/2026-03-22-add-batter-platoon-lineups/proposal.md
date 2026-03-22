## Why

The current public batter snapshot and team detail UI expose only one projected lineup, which hides how clubs arrange their starters against left-handed pitching and makes platoon-only starters hard to identify. Fangraphs now publishes dedicated platoon lineup pages with separate `vsR` and `vsL` go-to lineups, so the public release contract should reflect that richer source model instead of flattening batter data into a single order list.

## What Changes

- **BREAKING** Upgrade the public batter release contract in `depth-charts.json` from a single batter row array to a batter lineup object that carries separate `vsR` and `vsL` projected lineups.
- Update the Fangraphs batter ingest path to source projected go-to lineups from RosterResource platoon lineup pages rather than only the single depth chart lineup view.
- Preserve the existing public batter row metrics, identity fields, age, and recent history within each platoon lineup row so frontend consumers continue to use the approved snapshot rather than live joins.
- Add a consumer-facing platoon role marker for batters who start only versus right-handed or only versus left-handed pitchers.
- Update the team detail Batter section to let users switch between `vs RHP` and `vs LHP` lineups while keeping the existing table, sorting, and history expansion model.
- Extend regression and go/no-go checks so batter structural validation understands both lineup views and keeps current batter regression expectations anchored to the default `vsR` baseline.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: Public batter publication changes from a single lineup array to dual `vsR` and `vsL` batter lineups with consumer-facing platoon role metadata.
- `depth-charts-web-ui`: The team detail Batter section changes from a single static lineup table to a switchable `vs RHP` / `vs LHP` lineup view with platoon-only player labeling.

## Impact

- Affected data ingest and publish scripts: [`scripts/fangraphs_batter_sync.py`](/Users/ballad/Documents/Tools/notion/scripts/fangraphs_batter_sync.py), [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py), [`scripts/regression_checks.py`](/Users/ballad/Documents/Tools/notion/scripts/regression_checks.py), [`scripts/qa_go_no_go.py`](/Users/ballad/Documents/Tools/notion/scripts/qa_go_no_go.py)
- Affected public artifact contract: [`public/data/latest/depth-charts.json`](/Users/ballad/Documents/Tools/notion/public/data/latest/depth-charts.json)
- Affected frontend surface: [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js) and related Batter section styling
- External dependency: Fangraphs RosterResource `platoon-lineups/<team>` pages and their structured payload shape
