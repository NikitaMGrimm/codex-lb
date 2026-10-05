## Purpose

The quota bar includes use through Codex LB and external/direct use. The approximate indicator estimates the LB share of the current weekly or monthly cycle; it does not identify a person or directly measure subscription-credit charges.

## Accounting and calibration

Target costs begin at the current reset boundary, and the denominator is the latest upstream used percentage converted with the maintained plan capacity or configured Pro ratio. A first reading of 5% counts all 5%, even without a retained zero or 100%-used observation. A fresh unused cycle with no logged cost reports zero.

Select accounts known to be used only through LB under Settings → LB attribution → Clean reference accounts. Calibration uses only selected peers' fresh current-cycle quota use and successful costs over matching cycles, excluding the target itself. Empty selection disables positive-cost estimates; zero-cost estimates remain available. One positive peer reading suffices immediately, including a nonzero first reading. No reference emails or account IDs are hardcoded. The owner's two clean Team accounts predicted each other's current cycles at approximately 99% and 101% in read-only replay; older cycles showed workload drift, so the result remains approximate.

## Reset boundaries

A deadline advancing by at least one day recognizes a new cycle even when usage is equal or higher. A renewed deadline after expiry also confirms a reset. Expired latest deadlines and old-deadline regressions withhold estimates. Minute-scale deadline drift and small percentage corrections do not reset accounting. A meaningful drop to zero can mark a reset before metadata refreshes; a one-point same-deadline correction to zero waits for deadline confirmation.

Natural resets use the previous deadline when it lies between observations. Early resets use the new deadline minus the window duration if that fits between observations or a full-day deadline advance confirms renewal despite stale polls; otherwise the first fresh reset observation is the boundary. With no retained transition, a fresh deadline minus the duration identifies the initial cycle. Exact early-reset timing cannot be recovered when upstream metadata and observation spacing do not locate it.

## Limits and diagnostic values

Logged USD cost is an estimate from token prices, not a bill or measured subscription quota. Different model mixes, caching, direct use on peers, rounding, incomplete logs, and capacity-ratio assumptions bias calibration. Values above 100% deliberately remain visible to expose this mismatch. They must not be interpreted as proof of negative external use. If quota remains at zero while logged costs are positive, a percentage is undefined until upstream reports positive use. Calibration without any usable peer is also unavailable.

The Pro ratio affects attribution only. Polling remains separate from dashboard overview; the UI hides an expired cached estimate while new-cycle data refreshes.
