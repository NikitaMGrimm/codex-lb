# Explain unavailable LB attribution in the dashboard

## Why

The dashboard currently leaves the long-window quota area blank when an attribution estimate is unavailable. This makes an inconsistent estimate look like a rendering failure.

## What Changes

- Show a compact unavailable indicator next to weekly or monthly quota when the attribution API responds successfully without an estimate for that account.
- Explain that the estimate needs fresh quota observations, a full-quota baseline, and usable peer calibration, and that inconsistent calibration suppresses it.

## Impact

Dashboard presentation only. The estimator continues to suppress invalid percentages.
