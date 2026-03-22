## Why

The team detail page now carries richer public depth chart and injury content, but the current presentation still feels like a utilitarian internal data surface. Before committing to a full visual refresh, the project needs multiple in-browser style prototypes so the final direction can be chosen from real rendered UI rather than text descriptions.

## What Changes

- Create multiple visual style prototypes for `/team/:abbr` that keep the same public content, section order, and table-driven interaction model.
- Add a preview mechanism that lets reviewers switch between prototype styles while using the same live page structure and data.
- Refresh page-level styling for the team detail experience, including hero treatment, section containers, table polish, typography, color system, and lightweight motion.
- Keep the prototypes consumer-facing and compatible with the existing public release boundary, route structure, and responsive behavior.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `depth-charts-web-ui`: Extend the team detail UI requirements to support multiple visual style prototypes for comparison and to define the visual-refresh boundaries that preserve existing content behavior.

## Impact

- Affected code: [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js), [`public/styles.css`](/Users/ballad/Documents/Tools/notion/public/styles.css), and possibly [`public/index.html`](/Users/ballad/Documents/Tools/notion/public/index.html) for preview controls or theme wiring.
- Affected specs: delta spec for `depth-charts-web-ui`.
- User impact: reviewers can compare real team detail style options in-browser before selecting the final production visual direction.
