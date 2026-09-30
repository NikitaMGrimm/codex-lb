## Purpose

The long-window quota bar combines requests routed through Codex LB with requests made directly to OpenAI. The “via LB” indicator estimates the share associated with successful requests logged by Codex LB. It cannot identify an individual unless the account's LB use belongs to that person alone.

## Calculation and controls

The API counts quota growth since the latest observed 100% point, including growth after resets. It converts percentage growth to Codex LB subscription credits for each plan and window, then calibrates successful LB request USD cost against observed credits on other accounts. For example, a Pro account with 160 percentage points of observed weekly growth at a configured 20:1 ratio to a 7,560-credit Plus weekly quota has 241,920 effective observed credits. A $1,200 LB cost with a calibrated $0.01 per credit would imply 120,000 LB credits, or about 50% via LB.

The Pro ratio setting is optional and affects this estimate alone. When absent, the estimate uses the maintained Pro weekly credit capacity. A ratio of 20 uses 20 times the maintained Plus/Team weekly capacity. The endpoint is fetched separately once per minute; indexed baseline lookups and change-edge reads keep history work bounded.

## Limits and failure modes

Subscription credits are derived locally from the upstream usage percentage; LB request logs have USD cost but no measured subscription-credit amount. The estimator assumes the logged USD-to-credit relationship is comparable across reference and target traffic. Direct use on reference accounts, request-mix differences, missing costs, quota rounding, and usage polling delays can bias it. The API omits estimates that exceed observed use instead of presenting them as 100%. The setting does not reveal the true OpenAI plan limit or measure direct use.
