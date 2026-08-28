# upstream-proxy-routing Delta

## ADDED Requirements

### Requirement: Dispatch-only ownership may fail over before visible output

When an otherwise unpinned client-supplied Responses payload becomes
account-bound only because it was dispatched to the selected account, and that
account returns an existing failover-eligible failure before any response output
becomes visible, the service MUST release that dispatch-created ownership,
exclude the failed account, and retry the original payload on another eligible
account within the existing attempt and request budgets. The service MUST NOT
apply this exception to previous-response, turn-state, uploaded-file, or
single-account ownership, or after downstream-visible output.

#### Scenario: Nonportable full history survives a pre-visible quota failure

- **GIVEN** an unpinned client request contains history that is not provably account-neutral
- **AND** the first selected account returns a failover-eligible quota failure before visible output
- **WHEN** another account is eligible
- **THEN** the service releases only the ownership created by the failed dispatch
- **AND** it retries the original client payload on the other account
- **AND** subsequent soft affinity may re-anchor to the successful account

#### Scenario: Pre-existing hard ownership remains fail-closed

- **GIVEN** a request depends on a previous response, turn state, uploaded file, or single-account policy
- **WHEN** its required account fails
- **THEN** the service does not use dispatch-owner release to move the request to another account
