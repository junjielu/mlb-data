## Why

The current team detail page only shows the 2025 depth chart row for each player, which makes it hard to compare a current projected role with that player's recent performance in the same view. The public release contract also lacks a stable consumer-facing player identifier, which blocks clean row expansion and future player-level UI extensions.

## What Changes

- Add a stable public `playerId` field to published Batter, SP, and RP rows in `public/data/latest/depth-charts.json`.
- Extend published player rows with consumer-facing `history` data for seasons 2024 and 2023.
- Update the team detail page so each 2025 player row can be clicked to expand inline 2024 and 2023 history rows, and clicked again to collapse.
- Keep sorting behavior anchored to 2025 primary rows while expanded history rows remain attached to their owning player row.
- Continue excluding operator-only identity matching diagnostics, QA artifacts, and review metadata from the public release surface.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `depth-charts-data-pipeline`: The public depth charts release contract will expose consumer-facing `playerId` and recent history fields on published rows while continuing to exclude operator-only diagnostics.
- `depth-charts-web-ui`: The team detail page will support inline expansion of recent season history beneath each 2025 player row.

## Impact

- Affected code: `scripts/fangraphs_batter_sync.py`, `scripts/fangraphs_sp_sync.py`, `scripts/fangraphs_rp_sync.py`, `scripts/depth_charts_pipeline.py`, `public/app.js`, `public/styles.css`.
- Public data contract: `public/data/latest/depth-charts.json`.
- Runtime impact: additional Fangraphs historical data lookups during build generation and a larger public depth charts artifact.
- Documentation/spec impact: updates to `openspec/specs/depth-charts-data-pipeline/spec.md` and `openspec/specs/depth-charts-web-ui/spec.md`.
