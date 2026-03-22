## 1. Source Data

- [x] 1.1 Inspect the Fangraphs batter, SP, and RP source payloads to confirm the available age field name and format for each pipeline.
- [x] 1.2 Update `scripts/fangraphs_batter_sync.py`, `scripts/fangraphs_sp_sync.py`, and `scripts/fangraphs_rp_sync.py` to retain the player age value in the structured source rows.

## 2. Publish Pipeline

- [x] 2.1 Update `scripts/depth_charts_pipeline.py` so published Batter, SP, and RP rows carry a consumer-facing `age` field while keeping operator-only fields excluded from `public/data/latest/depth-charts.json`.
- [x] 2.2 Rebuild a candidate snapshot and verify QA/regression checks still pass with the age field present.

## 3. Frontend

- [x] 3.1 Update [public/app.js](/Users/ballad/Documents/Tools/notion/public/app.js) to render age inline to the right of player names for Batter, SP, and RP primary rows only.
- [x] 3.2 Add or adjust styles in [public/styles.css](/Users/ballad/Documents/Tools/notion/public/styles.css) so the inline age label stays readable on desktop and mobile without adding a new table column.

## 4. Verification

- [x] 4.1 Refresh `public/data/latest/depth-charts.json` with the new age field and verify a sample of batter and pitcher rows contain the expected published data.
- [x] 4.2 Preview `/team/:abbr` locally and confirm linked names, expandable history rows, and missing-age behavior all render as specified.
