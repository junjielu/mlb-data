## ADDED Requirements

### Requirement: Batter section supports simultaneous platoon comparison
The web UI SHALL render the team detail Batter section as a simultaneous platoon comparison surface so users can inspect the approved `vs RHP` and `vs LHP` batter views together without switching between them.

#### Scenario: Team detail page renders both handedness columns
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter section renders both the `vs RHP` and `vs LHP` views from the approved public snapshot at the same time
- **AND** the page MUST NOT require a lineup toggle control to access one of the handedness views

#### Scenario: Each handedness column shows starters and primary alternates together
- **WHEN** the Batter section renders a handedness column
- **THEN** the starter lineup for that handedness appears before the corresponding `Primary Alternates` group from the approved public snapshot
- **AND** both groups remain part of the same handedness comparison column

#### Scenario: Simultaneous platoon comparison remains usable on narrow screens
- **WHEN** the team detail page is rendered on a narrow viewport
- **THEN** the Batter section still shows both handedness views within the same page flow
- **AND** the layout may stack the handedness columns vertically instead of hiding one side behind a toggle

## MODIFIED Requirements

### Requirement: Batter platoon-only starters are labeled inline
The web UI SHALL surface platoon-only batter context directly in rendered Batter rows so users can tell when a starter or alternate appears only against one pitcher handedness.

#### Scenario: Right-handed-pitching-only batter row is labeled
- **WHEN** a rendered Batter row carries the public marker for a player who appears only against right-handed pitching in that row type
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs RHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Left-handed-pitching-only batter row is labeled
- **WHEN** a rendered Batter row carries the public marker for a player who appears only against left-handed pitching in that row type
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs LHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Shared-handedness batter row remains unlabeled in the name cell
- **WHEN** a rendered Batter row represents a player who appears in both handedness collections for that row type
- **THEN** the team detail page renders the linked player name without a platoon-only label
- **AND** it MUST NOT show a placeholder or neutral badge for the player

## REMOVED Requirements

### Requirement: Batter section supports platoon lineup view switching
**Reason**: The Batter experience now prioritizes direct side-by-side comparison, so a toggle-based active view is no longer the intended interaction model.
**Migration**: Render both handedness views together and read starters from `batter.lineups.<handedness>` plus primary alternates from `batter.alternates.<handedness>` instead of storing one active batter view in frontend state.
