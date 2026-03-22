## 1. Fangraphs pitcher ingestion

- [x] 1.1 Verify the Fangraphs source field names for pitcher `vFA` and `BABIP` in both current-season and history responses.
- [x] 1.2 Update `scripts/fangraphs_sp_sync.py` to normalize and emit `vfa` and `babip` alongside the existing SP public fields.
- [x] 1.3 Update `scripts/fangraphs_rp_sync.py` to normalize and emit `whip`, `location_plus`, `vfa`, and `babip` and stop carrying `k_pct` in the public RP row shape.

## 2. Public snapshot pipeline

- [x] 2.1 Update `scripts/depth_charts_pipeline.py` to publish the unified SP/RP metric contract on primary rows and remove public RP `k_pct`.
- [x] 2.2 Update pitcher history assembly in `scripts/depth_charts_pipeline.py` so SP and RP history rows both publish `whip`, `location_plus`, `vfa`, and `babip` with the unified metric order.
- [x] 2.3 Regenerate a candidate depth chart build and confirm the published pitcher row schema matches the new OpenSpec requirements.

## 3. Web UI presentation

- [x] 3.1 Update `public/app.js` so SP and RP share one pitcher column definition ordered as `Role`, `Name`, `Age`, `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, `BABIP`.
- [x] 3.2 Update any affected pitcher-table layout styles so the added `vFA` and `BABIP` columns remain readable on supported viewport sizes.
- [x] 3.3 Verify expanded SP and RP history rows stay aligned with the unified pitcher column model and use existing missing-value rendering.

## 4. Validation and release readiness

- [x] 4.1 Run regression and go/no-go checks against the updated candidate build and inspect for schema or publish-gate regressions.
- [x] 4.2 Preview the team detail UI locally and confirm SP/RP tables no longer render `K%` and do render `vFA` and `BABIP` after `Location+`.
- [x] 4.3 Update any affected operator or runbook documentation if implementation changes the expected pitcher public contract or verification workflow.
