## ADDED Requirements

### Requirement: VPS refresh preserves deployed migration history
The VPS refresh MUST retain the contents and parentage of deployed migration revisions and MUST converge with the refreshed usage-limit PR through a new merge revision.

#### Scenario: Existing VPS database upgrades
- **GIVEN** a VPS database at `20261005_180000_trusted_lb_calibration_references`
- **WHEN** it upgrades to the refreshed fork head
- **THEN** saved account policies and attribution settings are preserved
- **AND** both lineages converge at one head without rewriting applied revisions
