## ADDED Requirements

### Requirement: Team detail page supports visual prototype comparison
The web UI SHALL support multiple visual style prototypes for `/team/:abbr` so reviewers can compare rendered team detail directions against the same public data, content model, and route behavior before selecting a final refresh.

#### Scenario: Multiple team-detail style variants are available for review
- **WHEN** a reviewer opens a team detail page in prototype evaluation mode
- **THEN** the page provides at least two distinct visual style variants for comparison
- **AND** each variant renders the same selected team and public release data

#### Scenario: Prototype comparison does not require alternate page implementations
- **WHEN** a reviewer switches between available team-detail visual variants
- **THEN** the same team detail route and content structure remain in use
- **AND** the comparison MUST NOT depend on separate duplicate pages with divergent data wiring

### Requirement: Visual prototypes preserve team detail content behavior
The web UI MUST preserve the current team detail content contract while visual style prototypes are being compared.

#### Scenario: Section order and content scope remain unchanged in prototypes
- **WHEN** any team-detail visual prototype is rendered
- **THEN** Batter appears before SP
- **AND** SP appears before RP
- **AND** RP appears before Current Injury Report
- **AND** the prototype MUST NOT add operator-only diagnostics, new data summaries, or new public content sections

#### Scenario: Existing table interactions remain consistent across variants
- **WHEN** a reviewer sorts a table or expands a player row in any team-detail visual prototype
- **THEN** the page preserves the same sorting, expansion, source-link, and injury-state behaviors defined by the existing team detail requirements
- **AND** the visual variant only changes presentation rather than interaction semantics

### Requirement: Team detail visual refresh covers the core page surfaces
The web UI SHALL express each team-detail visual prototype through a coherent refresh of the existing core surfaces rather than isolated color changes.

#### Scenario: Prototype variants restyle the core page surfaces
- **WHEN** a team-detail visual prototype is rendered
- **THEN** the selected variant visibly changes the hero/header treatment, section surfaces, table styling, typography, and inline badges or labels
- **AND** the page remains readable and consumer-facing with the existing data density

#### Scenario: Prototype variants remain responsive
- **WHEN** a reviewer views any team-detail visual prototype on a narrow viewport
- **THEN** the page continues to support the existing responsive team-detail behaviors, including the batter handedness stacking model
- **AND** the refreshed styling MUST NOT make any section unusable on narrow screens
