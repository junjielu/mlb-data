## ADDED Requirements

### Requirement: SP and RP sections use the same pitcher column model
The web UI SHALL render the SP and RP tables on `/team/:abbr` with the same ordered consumer-facing pitcher columns: `Role`, `Name`, `Age`, `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, and `BABIP`.

#### Scenario: SP and RP render matching pitcher columns
- **WHEN** a user opens `/team/:abbr`
- **THEN** the SP section and the RP section both render columns in the order `Role`, `Name`, `Age`, `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, `BABIP`
- **AND** the RP table MUST NOT render a `K%` column

#### Scenario: Newly added pitcher metrics appear after Location+
- **WHEN** the team detail page renders SP or RP metrics from the approved public snapshot
- **THEN** `vFA` appears immediately after `Location+`
- **AND** `BABIP` appears immediately after `vFA`

#### Scenario: Missing unified pitcher metrics use existing missing-value treatment
- **WHEN** any SP or RP cell for `WHIP`, `Location+`, `vFA`, or `BABIP` is empty in the public snapshot
- **THEN** the corresponding table cell renders `--`
- **AND** the row remains visible in its original role position

### Requirement: Expanded pitcher history uses the unified pitcher metric columns
The web UI SHALL render expanded SP and RP history rows using the same unified pitcher column model as the corresponding primary row.

#### Scenario: Expanded SP and RP history stays aligned to the unified pitcher columns
- **WHEN** a user expands an SP or RP row on `/team/:abbr`
- **THEN** the rendered 2024 and 2023 history rows align to the same column structure as the owning SP or RP primary row
- **AND** the historical rows identify the season while preserving `vFA` and `BABIP` in the same relative positions as the primary row
