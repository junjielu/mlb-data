## Context

The current data pipeline already ingests Fangraphs lineup/rotation/bullpen data with team-level normalization in Python scripts, but operational delivery depends on writing content into Notion pages. This introduces instability around API writes, retry behavior, and hard-to-audit partial updates. The new approach keeps Fangraphs ingestion but switches the delivery surface to a web frontend that reads versioned static snapshots.

Constraints:
- Existing Python ingestion logic should be reused where possible to preserve current matching fixes (player ID fallback, loose name normalization).
- The first release should support the 2025 season data model already in use.
- Frontend must expose data freshness and warning state so consumers can trust/verify the snapshot.

Stakeholders:
- Data maintainer operating ingestion scripts.
- End users consuming MLB depth chart data.

## Goals / Non-Goals

**Goals:**
- Decouple ingestion from presentation by producing a unified snapshot file (`depth-charts.json`) and a quality report (`quality-report.json`).
- Provide a web UI with:
- Division-based team overview.
- Team detail tables in fixed order: Batter -> SP -> RP.
- Visible freshness and warning indicators.
- Enforce release gates before promoting a new snapshot to `latest`.

**Non-Goals:**
- Real-time streaming updates.
- Notion synchronization as part of normal delivery.
- Multi-season historical analytics in initial implementation.
- Rewriting ingestion in a new language/framework.

## Decisions

### 1) Static snapshot delivery over live API calls
- Decision: Frontend reads static JSON snapshots generated offline/periodically.
- Rationale: Removes runtime dependency on Fangraphs and avoids frontend instability from scraping/API variability.
- Alternative considered: Frontend calling a live backend API that fetches on request.
- Why not: Higher operational complexity and exposes users to transient source failures.

### 2) Keep Python ingestion scripts, add aggregation/publish layer
- Decision: Reuse `fangraphs_batter_sync.py`, `fangraphs_sp_sync.py`, `fangraphs_rp_sync.py` and add a pipeline step that merges outputs into unified schema.
- Rationale: Existing scripts already embed domain-specific matching fixes and 2025 validation assumptions.
- Alternative considered: Replace with a single new scraper from scratch.
- Why not: Regression risk and duplicated logic.

### 3) Introduce explicit quality report and publish gates
- Decision: Build emits `quality-report.json` with warning counts and blocking conditions; only successful gated builds publish to `public/data/latest`.
- Rationale: Prevents partial/invalid snapshots from becoming user-facing and provides auditable diagnostics.
- Alternative considered: Publish every run and rely on frontend best-effort rendering.
- Why not: Silent data degradation risk.

### 4) Frontend IA aligned to operational workflows
- Decision: Ship `/teams`, `/team/:abbr`, `/about-data` initially; `/compare` can follow once baseline is stable.
- Rationale: Covers discovery, detail inspection, and trust context with minimal initial surface.
- Alternative considered: Launch full comparison/advanced analytics at once.
- Why not: Delays stabilization of core read path.

### 5) Warning-first UI semantics
- Decision: Team/status badges and row-level missing indicators are first-class display elements, not hidden diagnostics.
- Rationale: Users frequently verify suspicious rows; surfacing quality state reduces manual triage time.
- Alternative considered: Keep warnings in logs only.
- Why not: Poor transparency for consumers.

## Risks / Trade-offs

- [Source schema drift at Fangraphs] -> Mitigation: Validation gates plus parser fallback hierarchy (exact name -> playerid -> normalized names); fail build on critical shape mismatch.
- [Static snapshot can become stale] -> Mitigation: Display `generatedAt`, `buildStatus`, and stale warning threshold in UI.
- [Initial frontend introduces new maintenance surface] -> Mitigation: Keep v1 UI minimal and data-driven; prioritize stable schema contract over visual complexity.
- [Partial missing stats remain for legitimately unavailable players] -> Mitigation: Mark as warnings (not hard failures) with consistent `--` display and explanatory tooltip.

## Migration Plan

1. Add snapshot aggregation step that merges existing batter/SP/RP outputs into unified schema.
2. Add quality report generation and gate evaluation.
3. Set up publish process:
- Write candidate snapshot/versioned artifacts.
- Promote to `latest` only when gates pass.
4. Build frontend pages against unified schema.
5. Validate against known regression checks (e.g., NYY SU7, TOR SU7, LAD Batter 5, ATH Batter 8).
6. Cut over consumer workflow from Notion pages to web UI.
7. Keep prior snapshot available for rollback by switching `latest` pointer.

## Open Questions

- Should initial release include `/compare`, or defer until baseline usage confirms stable core pages?
- What refresh cadence is desired (manual run, daily cron, or both)?
- Where should static artifacts be hosted (same frontend host, object storage + CDN, or repository-managed static files)?
- Do we need a hard SLA for maximum staleness before showing critical banner?
