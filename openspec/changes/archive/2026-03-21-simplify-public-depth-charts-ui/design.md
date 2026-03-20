## Context

The public depth charts site is already intentionally separated from the operator workflow: approved snapshots are published to `public/data/latest/`, while quality diagnostics and release decisions remain in candidate artifacts and QA outputs. The current frontend, however, still carries remnants of a maintenance-oriented interface. The teams page includes season selection, division filtering, search, and per-team roster counts. Both the teams and team detail pages show a status bar with season, source, updated timestamp, and build identifier. The main navigation also includes an `/about-data` page whose content explains ingestion and publication behavior rather than helping end users browse depth charts.

This change does not alter the data pipeline, snapshot schema, or publication workflow. It only narrows the public web contract so the static site behaves more like a reference surface and less like a small internal data browser.

Constraints:

- The site continues to consume `public/data/latest/depth-charts.json` as its only public data source.
- The season remains pinned to 2025 unless explicitly changed elsewhere.
- The schema major version remains unchanged.
- Internal QA, review, and release metadata still exist in pipeline artifacts, but are not part of the public browsing experience.

Stakeholders:

- End users browsing approved MLB depth charts.
- The maintainer who still needs operational visibility, but through pipeline artifacts rather than the public site.

## Goals / Non-Goals

**Goals:**

- Make `/teams` a simple division-grouped entry page without exploratory controls.
- Keep `/team/:abbr` focused on the team name and depth chart tables.
- Preserve only a minimal freshness signal for users who need basic recency context.
- Remove operator-style metadata and explanatory maintenance content from the public navigation experience.

**Non-Goals:**

- Changing published JSON structure or adding new frontend data fields.
- Altering the approval, review, or publish gating workflow.
- Introducing a replacement public explainer page with long-form data methodology content.
- Redesigning table sorting, row rendering, or team grouping beyond what is needed to simplify the public experience.

## Decisions

### 1) Treat the teams page as a navigation hub, not a data exploration tool

- Decision: `/teams` will remain grouped by division, but it will no longer expose season selection, division filtering, free-text player/team search, or roster-count summaries on team cards.
- Rationale: The site currently serves a single approved season and a fixed set of 30 teams, so exploration controls add interface weight without solving a real consumer need.
- Alternative considered: Keep controls but hide them behind a collapsed filter tray.
- Why not: The problem is not visual clutter alone; the controls frame the page as an analysis tool rather than a reference index.

### 2) Replace the status bar with localized freshness context

- Decision: Public pages will stop showing a shared status bar with season, source, updated timestamp, and build ID. Instead, the team detail page will carry at most a lightweight updated-time hint near the team content.
- Rationale: Users may benefit from basic recency awareness, but they do not need release-oriented metadata such as build IDs or source labels on every page.
- Alternative considered: Keep the status bar and simply hide the build ID.
- Why not: Even without the build ID, the full bar still foregrounds system metadata over team content.

### 3) Remove `/about-data` from the public primary experience

- Decision: The top-level navigation and public route set will no longer treat `/about-data` as part of the consumer-facing site.
- Rationale: The current content is primarily about ingestion, matching, and publication policy, which belongs to maintenance documentation rather than a public reference interface.
- Alternative considered: Keep the page but shorten its copy.
- Why not: Even a shortened version would still preserve a public information architecture slot for operator context that the product no longer wants to emphasize.

### 4) Keep simplification frontend-only

- Decision: This change will be implemented entirely in the static frontend layer and routing configuration without modifying pipeline artifacts or backend-style scripts.
- Rationale: The desired outcome is presentation-level simplification, not a contract change in the data system.
- Alternative considered: Remove metadata fields from published snapshots altogether.
- Why not: Those fields are still useful for maintenance workflows and can remain in the data while the UI chooses not to foreground them.

## Risks / Trade-offs

- [Users lose some context about what snapshot they are viewing] -> Mitigation: retain a weak updated-time signal on the team detail page.
- [Removing search and filters makes the teams page less powerful for power users] -> Mitigation: keep division grouping and direct team links so the primary browse path remains fast.
- [Removing `/about-data` may leave no public explanation path at all] -> Mitigation: treat that as intentional product scope; maintenance-oriented explanations remain available in repo docs and change artifacts.
- [Future multi-season support would need these decisions revisited] -> Mitigation: keep the simplification scoped to the current single-season product contract rather than presenting it as a permanent architectural constraint.

## Migration Plan

1. Update the public navigation and page rendering so `/teams` becomes a static division-grouped index without filters or search.
2. Remove the shared status bar from page rendering and reintroduce only a small updated-time treatment on the team detail page.
3. Remove `/about-data` from navigation and public routing behavior.
4. Validate that `/teams` and `/team/:abbr` still render correctly in the SPA and that direct route refresh works after route changes.

Rollback is straightforward: restore the previous frontend rendering and route configuration while leaving the published snapshot artifacts unchanged.

## Open Questions

- Should the lightweight updated-time hint appear only on `/team/:abbr`, or also in a very subtle form on `/teams`?
- If `/about-data` is removed, should unknown routes fall back directly to `/teams` more aggressively, or is the existing not-found behavior acceptable?
