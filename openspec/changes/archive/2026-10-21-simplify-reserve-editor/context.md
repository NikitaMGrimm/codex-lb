# Context: simplify the reserve editor

## Mapping rows to stored fields

The API keeps a default maximum-used percentage plus optional 5-hour and weekly overrides. The editor shows the *effective* reserve per window instead of the fields themselves:

| Account windows | Rows |
| --- | --- |
| 5-hour + weekly | 5-hour, Weekly |
| weekly only | Weekly |
| monthly only | Monthly (default) |
| unknown, or only nonstandard | All windows (default) |
| 5-hour + nonstandard/monthly | 5-hour, Other windows (default) |

On save, a standard row whose value equals the default it would inherit clears its override; any other value becomes an override. A blank row means no reserve; when a default exists, that needs an explicit full-use override (maximum used 100). If no default row is shown, the stored default is not sent, so it is retained. Clearing every row removes the policy, including overrides for windows the account no longer reports, because an enabled override without a matching observation fails closed.

Example: default 80, 5-hour 70, weekly 90 (reserves 20/30/10). The editor shows 5-hour 30 and Weekly 10; the inert 20 is not shown. Changing Weekly to 15 sends `{enabled: true, percent5H: 70, percentWeekly: 85}`.

## Preview

Usable = provider remaining − reserve, floored at zero, computed from the draft. A window is marked reached when remaining ≤ reserve (the admission rule `used ≥ cap`). A disabled policy shows the full remaining quota as usable.

## Known trade-off

Keeping an untouched window's reserve while the default changes needs an explicit override for that window. An enabled override requires a current matching observation, so if that window's last observation has expired, the account reports `data_unavailable` until a fresh matching observation arrives, even though the default alone would have treated the expired window as reset. This only arises when a default row is shown next to a standard window (a monthly, nonstandard, or unidentified window alongside 5-hour or weekly) and fails closed, so the editor accepts it rather than silently changing the reserve a row displays.
