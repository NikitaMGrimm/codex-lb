# Local audit

The September 29 audit reviews local head `41ec18a31` against its local main
ancestor `d4b00fd05`. The published PR has diverged; this work preserves the
checked-out scalar policy and leaves rebasing to a separate step.

Enabled policies need immediate selection invalidation after live observations.
Uncapped accounts still need the existing throttled invalidation for ranking
and status recovery. Removing that path changes behavior when the feature is off.

Authorization before admission cannot authorize dispatch after a wait. For
example, a socket can pass a 10% cap check, wait for a response-create slot,
then send after another turn raises observed usage to 12%. Dispatch must
recheck the policy and pending-request ownership, while already-sent turns
retain their settlement paths. Database failures must reject only the new turn.

Bridge policy reads must not hold the lock that the upstream reader needs to
complete other turns. This is separate from lease reacquisition, which still
needs atomic session accounting.

The policy remains observation-bound: upstream reporting and already-dispatched
work can overshoot the configured threshold. No new settings or dependencies
are needed for these fixes.
