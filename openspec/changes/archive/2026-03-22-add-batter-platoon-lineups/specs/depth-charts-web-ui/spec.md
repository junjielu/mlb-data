## ADDED Requirements

### Requirement: Batter section supports platoon lineup view switching
The web UI SHALL render the team detail Batter section as a switchable platoon lineup view so users can inspect projected starters against right-handed and left-handed pitching without leaving `/team/:abbr`.

#### Scenario: Batter section defaults to right-handed-pitching view
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter section initially renders the `vs RHP` lineup view from the approved public snapshot
- **AND** the page provides a visible control to switch the Batter section to the `vs LHP` lineup view

#### Scenario: User switches to left-handed-pitching view
- **WHEN** a user selects the `vs LHP` control in the Batter section
- **THEN** the Batter table rerenders using the approved `vsL` lineup rows for that team
- **AND** the existing Batter columns, sorting, missing-value rendering, and expandable history behavior remain available in the selected view

### Requirement: Batter platoon-only starters are labeled inline
The web UI SHALL surface platoon-only starter context directly in the Batter table so users can tell when a player starts only against one pitcher handedness.

#### Scenario: Right-handed-pitching-only starter is labeled
- **WHEN** a Batter row in the active lineup view carries the public marker for a player who starts only against right-handed pitching
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs RHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Left-handed-pitching-only starter is labeled
- **WHEN** a Batter row in the active lineup view carries the public marker for a player who starts only against left-handed pitching
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs LHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Everyday starter remains unlabeled in the name cell
- **WHEN** a Batter row represents a player who starts in both lineup views
- **THEN** the team detail page renders the linked player name without a platoon-only label
- **AND** it MUST NOT show a placeholder or neutral badge for the player
