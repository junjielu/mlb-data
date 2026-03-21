## ADDED Requirements

### Requirement: Batter table displays counting stats after position
The web UI SHALL display batter counting stats `R`, `HR`, `RBI`, and `SB` on the team detail page Batter table immediately after the `Position` column, keep `AVG`, `OBP`, and `SLG` ahead of `wRC+`, and place `wRC+` in the final Batter column.

#### Scenario: Team detail batter columns include counting stats
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter table columns appear in the order `Order`, `Name`, `Position`, `R`, `HR`, `RBI`, `SB`, `AVG`, `OBP`, `SLG`, `wRC+`
- **AND** each counting stat cell is rendered from the approved public `depth-charts.json` artifact rather than a live Fangraphs request

### Requirement: Newly added batter counting stats use existing missing-value treatment
The web UI MUST apply the existing missing metric presentation to batter counting stats `R`, `HR`, `RBI`, and `SB`.

#### Scenario: Missing batter counting stat presentation
- **WHEN** any of the newly added batter counting stat fields are empty in the public snapshot
- **THEN** the corresponding Batter table cell renders `--`
- **AND** the row remains visible in its original lineup order
