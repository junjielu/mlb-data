## ADDED Requirements

### Requirement: Public batter publication exposes handedness-specific alternates
The depth charts data pipeline SHALL publish the Batter section with handedness-specific public alternates derived from Fangraphs platoon-page `Bench` rows so consumers can inspect each lineup's primary bench context alongside the approved starter views.

#### Scenario: Public batter artifact includes alternates for both lineup views
- **WHEN** the pipeline publishes an approved public depth chart snapshot
- **THEN** each team's Batter section includes an `alternates` container with `vsR` and `vsL` collections
- **AND** those collections are published alongside the existing `lineups.vsR` and `lineups.vsL` starter views

#### Scenario: Only Fangraphs bench rows are promoted into public alternates
- **WHEN** the batter ingest parses non-starter rows from a Fangraphs platoon lineup page
- **THEN** only rows marked `Bench` are included in the public `alternates` collections
- **AND** projected injured-list rows or other non-bench statuses are excluded from the public alternates contract

#### Scenario: Alternate rows retain the existing public batter row shape
- **WHEN** a public batter alternate row is published under `alternates.vsR` or `alternates.vsL`
- **THEN** the row retains the existing consumer-facing batter metrics, player link, public player identifier, age, recent history, and platoon role fields
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata in alternate rows

## MODIFIED Requirements

### Requirement: Public batter rows include consumer-facing platoon role markers
The depth charts data pipeline SHALL derive a lightweight consumer-facing platoon role marker on published batter rows across both starter lineups and alternates so consumers can distinguish one-sided platoon usage from shared handedness usage without comparing every collection manually.

#### Scenario: Batter row is labeled as right-handed-pitching-only option
- **WHEN** a published batter appears only in the `vsR` collection of a given batter row type for the same team
- **THEN** the public row includes a platoon role marker indicating that the player is published only against right-handed pitching

#### Scenario: Batter row is labeled as left-handed-pitching-only option
- **WHEN** a published batter appears only in the `vsL` collection of a given batter row type for the same team
- **THEN** the public row includes a platoon role marker indicating that the player is published only against left-handed pitching

#### Scenario: Shared handedness option remains unlabeled
- **WHEN** a published batter appears in both `vsR` and `vsL` collections for the same team and batter row type
- **THEN** the public row omits the one-sided platoon marker
- **AND** the consumer-facing artifact remains visually quiet for non-platoon entries

### Requirement: Batter publish gating validates both platoon lineup views
The depth charts data pipeline MUST validate structural completeness of both published batter platoon lineup views and the presence of handedness-specific alternates containers before promoting a new public snapshot.

#### Scenario: Missing platoon lineup view blocks publish
- **WHEN** a candidate snapshot is missing either the `vsR` batter lineup or the `vsL` batter lineup for any team
- **THEN** the candidate is marked as not publishable
- **AND** `public/data/latest/depth-charts.json` remains unchanged

#### Scenario: Missing alternates container blocks publish
- **WHEN** a candidate snapshot omits `alternates.vsR` or `alternates.vsL` for any team's Batter section
- **THEN** the candidate is marked as not publishable
- **AND** `public/data/latest/depth-charts.json` remains unchanged

#### Scenario: Existing batter regression baseline remains anchored to default right-handed starter view
- **WHEN** regression checks evaluate known batter lineup fixtures after public alternates are introduced
- **THEN** the existing batter regression cases read from the default `lineups.vsR` starter view
- **AND** the new structural validation still requires both starter lineup views and both alternates collections to be present
