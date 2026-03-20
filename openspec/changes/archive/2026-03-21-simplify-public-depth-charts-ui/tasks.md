## 1. Simplify Teams Overview

- [x] 1.1 Remove the shared status-bar rendering from the teams page in `public/app.js`.
- [x] 1.2 Remove season selection, division filtering, and free-text search controls from the teams page flow in `public/app.js`.
- [x] 1.3 Remove roster-count summary text from team cards while preserving division grouping and team links.

## 2. Simplify Team Detail And Navigation

- [x] 2.1 Replace the current page-level status bar on `/team/:abbr` with a lightweight updated-time treatment near the team content.
- [x] 2.2 Remove `/about-data` from the top navigation and update route handling in `public/app.js` and `public/index.html` so the public experience centers on `/teams` and `/team/:abbr`.
- [x] 2.3 Update `vercel.json` if needed so SPA rewrites match the reduced public route set.

## 3. Polish And Validate

- [x] 3.1 Adjust `public/styles.css` so the simplified pages still feel intentional after the filter/status/about elements are removed.
- [x] 3.2 Validate that `/teams` and `/team/:abbr` render correctly with `public/data/latest/depth-charts.json`, including missing-metric rendering and external player links.
- [x] 3.3 Verify direct navigation and refresh behavior for `/teams` and `/team/:abbr` after the route simplification.
