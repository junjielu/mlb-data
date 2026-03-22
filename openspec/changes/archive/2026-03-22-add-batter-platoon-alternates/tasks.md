## 1. Batter ingest and publish contract

- [x] 1.1 Update [`scripts/fangraphs_batter_sync.py`](/Users/ballad/Documents/Tools/notion/scripts/fangraphs_batter_sync.py) to parse handedness-specific `Bench` rows from Fangraphs platoon payloads while excluding non-bench statuses from the new public alternates path.
- [x] 1.2 Extend the batter source artifact shape so each team carries `alternates.vsR` and `alternates.vsL` alongside the existing starter lineups.
- [x] 1.3 Update [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py) sanitization and publish logic to preserve the new alternates collections in `public/data/latest/depth-charts.json`.

## 2. Platoon labels and validation

- [x] 2.1 Update batter platoon-role derivation so starter rows and alternate rows both receive the correct consumer-facing `platoonRole` markers.
- [x] 2.2 Extend publish gating in [`scripts/depth_charts_pipeline.py`](/Users/ballad/Documents/Tools/notion/scripts/depth_charts_pipeline.py) so Batter requires both starter lineup views and both alternates collections before publish.
- [x] 2.3 Update [`scripts/regression_checks.py`](/Users/ballad/Documents/Tools/notion/scripts/regression_checks.py) and [`scripts/qa_go_no_go.py`](/Users/ballad/Documents/Tools/notion/scripts/qa_go_no_go.py) to validate the new batter contract while keeping existing regression fixtures anchored to starter `lineups.vsR`.

## 3. Batter UI comparison layout

- [x] 3.1 Refactor [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js) so the Batter section renders simultaneous `vs RHP` and `vs LHP` columns instead of a toggle-based active view.
- [x] 3.2 Render each handedness column with the starter lineup followed by a `Primary Alternates` group sourced from `batter.alternates.<handedness>`.
- [x] 3.3 Update [`public/styles.css`](/Users/ballad/Documents/Tools/notion/public/styles.css) so the paired platoon layout remains readable on desktop and stacks cleanly on narrower screens without hiding either handedness view.

## 4. Verification and release readiness

- [x] 4.1 Build a fresh candidate snapshot and verify the published batter artifact contains `lineups` plus `alternates` for both handedness views.
- [x] 4.2 Run regression and go/no-go checks and confirm no new gating failures are introduced by alternates.
- [x] 4.3 Preview `/team/:abbr` locally to verify simultaneous platoon comparison, primary alternates rendering, platoon labels, and responsive behavior before publish.
