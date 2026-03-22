## ADDED Requirements

### Requirement: Public batter publication exposes platoon lineup views
The depth charts data pipeline SHALL publish the Batter section as a consumer-facing platoon lineup container that preserves separate projected go-to lineups against right-handed and left-handed pitching within the approved public `depth-charts.json` artifact.

#### Scenario: Public batter artifact includes both lineup views
- **WHEN** the pipeline publishes an approved public depth chart snapshot
- **THEN** each team's Batter section includes a `vsR` lineup view and a `vsL` lineup view
- **AND** each lineup view contains the ordered projected batter rows for that handedness

#### Scenario: Existing public batter row fields remain available in each lineup view
- **WHEN** a public batter lineup row is published under `vsR` or `vsL`
- **THEN** the row retains the existing consumer-facing batter metrics, player link, public player identifier, age, and recent history fields
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata in either lineup view

### Requirement: Public batter rows include consumer-facing platoon role markers
The depth charts data pipeline SHALL derive a lightweight consumer-facing platoon role marker on published batter lineup rows so consumers can distinguish one-sided starters from everyday starters without inspecting both lineup views manually.

#### Scenario: Batter row is labeled as right-handed-pitching-only starter
- **WHEN** a published batter appears in the `vsR` lineup and is absent from the `vsL` lineup for the same team
- **THEN** the public row includes a platoon role marker indicating that the player starts only against right-handed pitching

#### Scenario: Batter row is labeled as left-handed-pitching-only starter
- **WHEN** a published batter appears in the `vsL` lineup and is absent from the `vsR` lineup for the same team
- **THEN** the public row includes a platoon role marker indicating that the player starts only against left-handed pitching

#### Scenario: Everyday starter remains unlabeled
- **WHEN** a published batter appears in both `vsR` and `vsL` lineup views for the same team
- **THEN** the public row omits the one-sided platoon marker
- **AND** the consumer-facing artifact remains visually quiet for non-platoon starters

### Requirement: Batter publish gating validates both platoon lineup views
The depth charts data pipeline MUST validate structural completeness of both published batter platoon lineup views before promoting a new public snapshot.

#### Scenario: Missing platoon lineup view blocks publish
- **WHEN** a candidate snapshot is missing either the `vsR` batter lineup or the `vsL` batter lineup for any team
- **THEN** the candidate is marked as not publishable
- **AND** `public/data/latest/depth-charts.json` remains unchanged

#### Scenario: Existing batter regression baseline remains anchored to default right-handed view
- **WHEN** regression checks evaluate known batter lineup fixtures after platoon publication is introduced
- **THEN** the existing batter regression cases read from the default `vsR` lineup view
- **AND** the new structural validation still requires both lineup views to be present
