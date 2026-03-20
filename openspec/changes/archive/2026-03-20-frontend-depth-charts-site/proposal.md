## Why

The current workflow depends on writing depth chart data into Notion, which has proven unstable and hard to validate end-to-end when sync retries or partial failures occur. We need a more reliable delivery path where data generation and presentation are decoupled, with clear quality visibility and deterministic output.

## What Changes

- Replace Notion as the primary output target with a web-first delivery model.
- Keep Fangraphs ingestion and normalization, but publish a unified static JSON snapshot for frontend consumption.
- Introduce a quality report artifact to surface missing rows, ordering issues, and warning counts per team.
- Build a frontend experience with:
- Division-based team overview page.
- Team detail page with fixed section order: Batter -> SP -> RP.
- Data status/recency and warning visibility.
- Add release gates so only validated snapshots are promoted to the latest served dataset.

## Capabilities

### New Capabilities
- `depth-charts-data-pipeline`: Generate, validate, version, and publish unified depth chart snapshots (plus quality report) from Fangraphs sources.
- `depth-charts-web-ui`: Render MLB depth chart data in a web interface with team overview, team detail, and data quality/status visibility.

### Modified Capabilities
- None.

## Impact

- Affected code:
- `scripts/fangraphs_batter_sync.py`
- `scripts/fangraphs_sp_sync.py`
- `scripts/fangraphs_rp_sync.py`
- New frontend project files (to be introduced).
- Removed dependency on Notion page content as the delivery surface for regular data consumers.
- New artifacts and workflows for snapshot publication and release gating.
- Operational impact: troubleshooting shifts from Notion write diagnostics to snapshot build/quality diagnostics.
