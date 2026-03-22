## Context

The current `/team/:abbr` page already exposes the right public content and interaction model: fixed sections, table-based comparisons, expandable player history, and a separate current injury report. The problem is visual rather than structural. Reviewers need to compare multiple rendered style directions against the same data and markup before choosing one for the production refresh.

This change stays inside the current public contract:

- No changes to `depth-charts.json` or `injuries.json`.
- No changes to section order, routing, or consumer-facing data scope.
- No operator or QA metadata exposed in the browser.
- No dependency on external design systems or runtime theming libraries.

The affected implementation is localized to the static frontend surface in [`public/app.js`](/Users/ballad/Documents/Tools/notion/public/app.js), [`public/styles.css`](/Users/ballad/Documents/Tools/notion/public/styles.css), and possibly [`public/index.html`](/Users/ballad/Documents/Tools/notion/public/index.html).

## Goals / Non-Goals

**Goals:**

- Allow reviewers to compare multiple team-detail visual prototypes in the browser using the same live page content and data.
- Keep the prototype mechanism narrow so the page can switch style variants without duplicating business logic or markup generation.
- Improve the visual quality of the page through styling changes to the hero, section surfaces, tables, typography, badges, and motion.
- Preserve responsive behavior and existing table interactions while styles change.

**Non-Goals:**

- Reworking the information architecture of the team detail page.
- Changing public data schema, section order, or adding new data summaries.
- Extending multi-style preview support to `/teams` or other routes in this change.
- Introducing persistent user theme settings or a site-wide theming framework.

## Decisions

### Use a page-scoped style variant switch instead of duplicated routes

The prototype comparison should reuse the same `/team/:abbr` rendering path and switch only the visual variant. A page-scoped variant signal keeps the comparison honest because every prototype is tested against identical content, DOM structure, and interactions.

Alternatives considered:

- Separate preview routes per style: simpler mentally, but duplicates routing behavior and increases drift risk.
- Separate HTML mockups: faster for ideation, but not useful for validating the real data-heavy page.

### Keep variant differences primarily in CSS, with minimal JS for preview wiring

The refresh is visual, so most divergence should live in CSS tokens, container classes, and section-specific styling. JavaScript should only provide the preview control and apply the active style variant at page render time.

Alternatives considered:

- Distinct markup per style: allows more freedom, but makes prototype comparison noisy and shifts the work toward layout rewrites.
- Full design-token system refactor first: cleaner long term, but too large for a bounded prototype comparison change.

### Limit prototype scope to the team detail page

The user concern is specifically the team detail experience. Restricting experiments to that route keeps the change reviewable and avoids unplanned redesign of the overview page.

Alternatives considered:

- Apply prototypes across the whole site immediately: broader visual consistency, but unnecessary for deciding the team-detail direction.

### Treat existing content behavior as invariant during prototype evaluation

Sorting, expansion, separate injury empty/unavailable states, source links, and responsive platoon stacking must behave the same across all variants. This isolates visual quality from behavioral regressions.

Alternatives considered:

- Allow prototypes to alter interactions: provides more freedom, but makes it harder to compare style choices independently from UX changes.

## Risks / Trade-offs

- [Prototype styling leaks into behavior changes] → Keep spec language explicit that prototypes preserve content model, section order, and table interactions.
- [CSS complexity increases with multiple variants] → Use a constrained variant model with shared base styles plus variant-specific overrides instead of copy-pasted rule blocks.
- [Reviewers prefer visual elements that are expensive to maintain] → Prototype with real code and responsive states so decisions are made against implementation reality.
- [Preview controls accidentally become production UI] → Scope preview controls to prototype evaluation only and define removal or finalization in follow-up implementation tasks.

## Migration Plan

1. Introduce the team-detail variant mechanism and render multiple selectable visual prototypes in development/preview.
2. Validate all variants against the same real snapshot data and current responsive/table behaviors.
3. Select one direction for the final production visual refresh.
4. Remove unused prototype styles and preview-only controls when converging on the final implementation.

Rollback is low risk because the current page structure and data loading flow remain intact. Reverting the variant wiring and prototype CSS restores the existing presentation.

## Open Questions

- How many style variants should be implemented in the first comparison round: two or three?
- Should preview switching use a query parameter, a temporary on-page control, or a dev-only toggle?
- Once a direction is chosen, should the overview page receive a follow-up refresh for visual consistency or remain unchanged?
