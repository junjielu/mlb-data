## Why

The public depth charts site still carries interface elements that are useful to operators but unnecessary for ordinary users, including build-oriented metadata, filtering controls, search, and a dedicated data-explainer page. That makes the frontend feel more like a maintenance tool than a clean reference surface for browsing MLB depth charts.

We want the published site to focus on a simpler user job: pick a team and view its depth chart. Operational context can remain in pipeline artifacts and QA outputs instead of the production UI.

## What Changes

- Simplify the public teams overview page so it serves as a static navigation surface grouped by division.
- Remove public UI elements that imply data exploration or release diagnostics, including season selection, division filtering, player search, and roster-count summaries on team cards.
- Remove the top status bar metadata from public pages instead of showing season, source, updated timestamp, and build identifier together.
- Keep a lightweight freshness signal in the team detail experience, but reduce it to a minimal updated-time presentation rather than a build/status banner.
- Remove the `/about-data` page from the main public experience because its current content is operator-oriented rather than consumer-oriented.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `depth-charts-web-ui`: narrow the public frontend contract to a cleaner consumer-facing browsing experience with minimal freshness metadata and without operator-style page controls or explanatory maintenance content.

## Impact

- Affected code: `public/app.js`, `public/index.html`, `public/styles.css`, and possibly `vercel.json` if `/about-data` is removed from the public route set.
- Affected behavior: `/teams`, `/team/:abbr`, and navigation structure across the static site.
- Affected product contract: the production UI becomes a reference-style surface for viewing approved depth charts, while pipeline/release details remain outside the public frontend.
