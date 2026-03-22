## ADDED Requirements

### Requirement: Team detail player names display age inline
The web UI SHALL display a player's age inline to the right of the linked player name on Batter, SP, and RP primary rows on `/team/:abbr`.

#### Scenario: Batter row shows age beside name
- **WHEN** a Batter primary row has an age value in the approved public snapshot
- **THEN** the team detail page renders that age inline to the right of the player's linked name
- **AND** the age display remains part of the same name cell rather than a separate table column

#### Scenario: Pitcher rows show age beside name
- **WHEN** an SP or RP primary row has an age value in the approved public snapshot
- **THEN** the team detail page renders that age inline to the right of the player's linked name
- **AND** the existing role/order columns and metric columns remain unchanged

#### Scenario: Missing age stays visually quiet
- **WHEN** a Batter, SP, or RP primary row has no age value in the public snapshot
- **THEN** the team detail page renders the linked player name without an age label
- **AND** it MUST NOT show a missing-value placeholder beside the name
