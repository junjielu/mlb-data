## 1. Fangraphs Batter Ingest

- [x] 1.1 Update [`scripts/fangraphs_batter_sync.py`](/Users/ballad/Documents/Tools/notion/scripts/fangraphs_batter_sync.py) to source batter lineup membership from Fangraphs RosterResource platoon lineup pages and capture both `vsR` and `vsL` projected lineups for each team.
- [x] 1.2 Preserve the existing public batter row fields within each lineup row and emit any additional source data needed to derive consumer-facing platoon role markers during publish.
- [x] 1.3 Validate the batter sync output shape for all 30 teams, including structural completeness of both lineup views and representative player-link / player-id coverage.

## 2. Publish Pipeline And Validation

- [x] 2.1 Update [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py) so the public batter contract publishes a batter lineup container with `defaultView`, `lineups.vsR`, and `lineups.vsL`.
- [x] 2.2 Derive and publish a consumer-facing platoon role marker for one-sided batter starters while keeping operator-only diagnostics excluded from the public artifact.
- [x] 2.3 Extend quality evaluation, regression checks, and go/no-go validation in [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py), [`scripts/regression_checks.py`](/Users/ballad/Documents/Tools/notion/scripts/regression_checks.py), and [`scripts/qa_go_no_go.py`](/Users/ballad/Documents/Tools/notion/scripts/qa_go_no_go.py) so both batter lineup views are required structurally and legacy batter regression fixtures read from `vsR`.

## 3. Team Detail UI

- [x] 3.1 Update [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js) to read the new batter lineup container, default to `vs RHP`, and rerender the Batter table when users switch between `vs RHP` and `vs LHP`.
- [x] 3.2 Preserve existing Batter table behavior in the selected lineup view, including sorting, missing-value rendering, and expandable recent history, while ensuring row identity and expanded state remain stable per lineup view.
- [x] 3.3 Render platoon-only starter labels inline beside batter names and adjust related styling in the frontend so the labels remain secondary to the player name and metrics.

## 4. Verification And Release

- [x] 4.1 Build a new depth charts candidate and verify the candidate and public `depth-charts.json` artifacts contain both batter lineup views and consumer-facing platoon role markers only.
- [x] 4.2 Run [`scripts/regression_checks.py`](/Users/ballad/Documents/Tools/notion/scripts/regression_checks.py) and [`scripts/qa_go_no_go.py`](/Users/ballad/Documents/Tools/notion/scripts/qa_go_no_go.py) against the updated candidate and confirm the new batter structural gates and existing `vsR` regression fixtures pass.
- [x] 4.3 Preview `/team/:abbr` locally to confirm the Batter section view switcher, platoon labels, and existing SP/RP/Injury sections render correctly before publishing the updated snapshot.
