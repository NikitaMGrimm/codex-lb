## Purpose

The VPS fork keeps migrations that have already run on its production database while integrating upstream releases. Alembic must see one upgrade path from the deployed revision to the refreshed image's head.

## Example and failure mode

The database can be at `20260930_000000_pro_weekly_attribution_ratio` while upstream has reached `20260918_000000_merge_scim_and_overflow_heads`. A no-op merge revision joins those histories. Rewriting either deployed migration would make existing databases and fresh databases disagree about what a revision means; a missing join would leave multiple heads and block a safe deployment.
