## 1. Variant Wiring

- [x] 1.1 Add a team-detail preview variant mechanism that switches visual styles without creating duplicate team detail routes or duplicate data-loading logic.
- [x] 1.2 Scope the preview mechanism to `/team/:abbr` so the current `/teams` page behavior remains unchanged during prototype evaluation.
- [x] 1.3 Ensure the active visual variant can be changed during review while preserving the current team selection and route behavior.

## 2. Prototype Style Implementation

- [x] 2.1 Implement the first team-detail visual prototype with a distinct hero, section surface, table, typography, and badge treatment.
- [x] 2.2 Implement the second team-detail visual prototype with a meaningfully different visual language while preserving the same content structure and table interactions.
- [x] 2.3 If a third prototype is included, implement it as a distinct style direction rather than a minor palette variation of the first two.
- [x] 2.4 Keep variant-specific styling layered on top of shared base styles so sorting, expansion, source links, and injury-state rendering continue to use the same markup and behavior.

## 3. Responsive and Interaction Validation

- [x] 3.1 Verify each prototype preserves the existing Batter, SP, RP, and Current Injury Report section order and content scope.
- [x] 3.2 Verify each prototype preserves current table sorting, expandable history rows, source links, and distinct injury empty/unavailable states.
- [x] 3.3 Verify each prototype remains usable on narrow screens, including stacked batter handedness views and readable injury updates.

## 4. Selection Readiness

- [x] 4.1 Document how reviewers should access and compare the available team-detail style variants in the browser.
- [x] 4.2 Capture the chosen direction and identify which prototype-only controls or unused styles must be removed when converging on the final production refresh.
