## ADDED Requirements

### Requirement: Public depth chart rows expose consumer-facing player identity
The depth charts data pipeline SHALL expose a stable consumer-facing `playerId` on each published Batter, SP, and RP row in the public `depth-charts.json` release artifact without exposing operator-only identity resolution diagnostics.

#### Scenario: Published row includes public player identifier
- **WHEN** a public `depth-charts.json` release is generated
- **THEN** each published Batter, SP, and RP row includes a `playerId` field
- **AND** the published row MUST NOT expose operator-only identity matching evidence such as `match_method`, `source_player_id`, or `matched_player_id`

### Requirement: Public depth chart rows include recent season history
The depth charts data pipeline SHALL publish recent season history for each public Batter, SP, and RP row as consumer-facing season entries for 2024 and 2023.

#### Scenario: Published row carries ordered recent history
- **WHEN** recent history is available for a published player row
- **THEN** the row includes a `history` collection with season entries for 2024 and 2023
- **AND** the entries are ordered from most recent season to least recent season

#### Scenario: Historical season entries remain consumer-facing
- **WHEN** a public historical season entry is published
- **THEN** it contains only the season label and consumer-facing baseball metrics needed by the web UI
- **AND** it MUST NOT include operator diagnostics, review metadata, or QA-only fields

#### Scenario: Missing historical values do not block publication
- **WHEN** one or more historical metric values are unavailable for a row's 2024 or 2023 history entry
- **THEN** the release artifact may leave those metric fields empty
- **AND** the row remains publishable without adding operator-only explanation fields to the public contract
