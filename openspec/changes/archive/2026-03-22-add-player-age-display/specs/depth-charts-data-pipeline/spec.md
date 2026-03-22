## ADDED Requirements

### Requirement: Public depth chart rows retain Fangraphs player age
The depth charts data pipeline SHALL retain each Fangraphs player row's current age on public Batter, SP, and RP rows in the published `depth-charts.json` artifact.

#### Scenario: Public release rows include age on primary players
- **WHEN** the pipeline builds and publishes a Batter, SP, or RP row from the Fangraphs source data
- **THEN** the published primary row includes an `age` field sourced from the parsed Fangraphs player row
- **AND** the age field is available for frontend consumption alongside the existing public player fields

#### Scenario: Missing age does not expose operator-only metadata
- **WHEN** Fangraphs does not provide a usable age value for a published Batter, SP, or RP row
- **THEN** the public row may leave the `age` field empty
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata to explain the missing age
