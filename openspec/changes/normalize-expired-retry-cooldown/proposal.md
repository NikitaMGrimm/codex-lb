# Normalize expired durable retry cooldowns

## Summary

An expired durable retry-circuit cooldown first observed after expiry must
reload as open, while an episode this worker observed cooling must still make
the normal one-probe half-open transition when it expires.

## What Changes

- Map an elapsed or absent durable cooldown first observed after expiry to the
  zero in-memory deadline.
- Preserve one-probe half-open admission for a previously observed active
  episode and retain that lease across equal-version reloads.
- Clear leftover probe leases when a future cooldown or replacement episode is
  adopted.
- Preserve future cooldown deadlines and all existing threshold, persistence,
  ownership, and backoff behavior.

## Impact

This is an internal retry-circuit admission fix. It adds no setting, schema,
wire-format, or operator action.
