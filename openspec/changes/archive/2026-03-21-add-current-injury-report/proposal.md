## Why

The current team pages only expose the pinned 2025 depth chart snapshot, which leaves users without current availability context when interpreting a club's roster outlook. Adding Fangraphs current-season injury information fills that gap without turning injury data into a publish-blocking dependency for the core depth chart release flow.

## What Changes

- Add a standalone current injury report data flow that pulls Fangraphs RosterResource injury data by team and publishes an approved latest snapshot separate from the existing depth chart pipeline.
- Extend team detail pages to display a `Current Injury Report` section alongside Batter, SP, and RP while keeping injuries as display-only context rather than roster-row overrides.
- Preserve Fangraphs injury source fields in the published injury dataset while presenting a lighter public view focused on player identity, status, and latest update text.
- Keep existing depth chart publish gating unchanged; injury refresh failures MUST retain the last published injury snapshot instead of blocking depth chart releases.

## Capabilities

### New Capabilities
- `current-injury-report-data`: Fetch, validate, publish, and retain a standalone current-season injury report snapshot sourced from Fangraphs RosterResource.

### Modified Capabilities
- `depth-charts-web-ui`: Team detail pages gain a current injury section and separate freshness context for current-season injury data versus the pinned 2025 depth chart snapshot.

## Impact

- Affected code: Fangraphs sync scripts, static data publishing pipeline, `public/data/latest/`, and the team detail rendering in `public/app.js` and related UI assets.
- Affected systems: Fangraphs RosterResource injury-report pages, Vercel-served static JSON artifacts, and public team detail pages.
- Dependencies: Continued reliance on Fangraphs as an external source, with a new requirement to tolerate stale injury data when current fetches fail.
