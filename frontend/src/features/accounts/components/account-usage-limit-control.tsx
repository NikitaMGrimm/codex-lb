import { Gauge, Trash2 } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import type {
  AccountSummary,
  AccountUsageLimitState,
  AccountUsageLimitUpdateRequest,
} from "@/features/accounts/schemas";

type AccountUsageLimitControlProps = {
  account: AccountSummary;
  busy: boolean;
  readOnly: boolean;
  onChange: (
    accountId: string,
    update: AccountUsageLimitUpdateRequest,
  ) => void;
};

export function AccountUsageLimitControl({
  account,
  busy,
  readOnly,
  onChange,
}: AccountUsageLimitControlProps) {
  const configuredPercent = account.usageLimitPercent ?? null;
  const [draft, setDraft] = useState(
    configuredPercent === null ? "" : formatPercent(configuredPercent),
  );
  const parsedDraft = Number(draft);
  const validDraft =
    draft.trim() !== "" &&
    Number.isFinite(parsedDraft) &&
    parsedDraft > 0 &&
    parsedDraft <= 100;
  const draftChanged =
    configuredPercent === null || parsedDraft !== configuredPercent;
  const disabled = busy || readOnly;
  const inputId = `usage-limit-percent-${account.accountId}`;

  const save = () => {
    if (!validDraft) {
      return;
    }
    onChange(account.accountId, {
      enabled:
        configuredPercent === null
          ? true
          : (account.usageLimitEnabled ?? false),
      percent: parsedDraft,
    });
  };

  return (
    <section className="space-y-3 rounded-md border bg-muted/30 p-3" aria-label="Account usage limit">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2 text-sm font-medium">
          <Gauge className="h-4 w-4 shrink-0 text-muted-foreground" />
          Usage limit
        </div>
        {configuredPercent !== null ? (
          <div className="flex items-center gap-2">
            <UsageLimitStateBadge state={account.usageLimitState ?? "disabled"} />
            <Switch
              aria-label="Enable usage limit"
              checked={account.usageLimitEnabled ?? false}
              disabled={disabled}
              onCheckedChange={(enabled) =>
                onChange(account.accountId, {
                  enabled,
                  percent: configuredPercent,
                })
              }
            />
          </div>
        ) : null}
      </div>

      {configuredPercent !== null ? (
        <p className="text-xs font-medium">
          {formatPercent(configuredPercent)}% maximum used · {formatPercent(100 - configuredPercent)}% reserved
        </p>
      ) : (
        <p className="text-xs text-muted-foreground">
          Set the maximum share of standard quota Codex LB may use. The remainder stays reserved.
        </p>
      )}

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <label className="min-w-0 flex-1 space-y-1" htmlFor={inputId}>
          <span className="text-xs font-medium">Maximum used percent</span>
          <div className="relative">
            <Input
              id={inputId}
              aria-label="Maximum used percent"
              className="h-8 pr-8 text-sm"
              type="number"
              inputMode="decimal"
              min="0"
              max="100"
              step="any"
              placeholder="10"
              value={draft}
              disabled={disabled}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  save();
                }
              }}
            />
            <span className="pointer-events-none absolute inset-y-0 right-2 flex items-center text-xs text-muted-foreground">
              %
            </span>
          </div>
        </label>
        <Button
          type="button"
          size="sm"
          className="h-8 text-xs"
          disabled={disabled || !validDraft || !draftChanged}
          onClick={save}
        >
          {configuredPercent === null ? "Set and enable" : "Save"}
        </Button>
        {configuredPercent !== null ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="h-8 gap-1.5 text-xs"
            disabled={disabled}
            onClick={() =>
              onChange(account.accountId, {
                enabled: false,
                percent: null,
              })
            }
          >
            <Trash2 className="h-3.5 w-3.5" />
            Remove
          </Button>
        ) : null}
      </div>

      {validDraft ? (
        <p className="text-xs text-muted-foreground">
          {formatPercent(parsedDraft)}% maximum used · {formatPercent(100 - parsedDraft)}% reserved
        </p>
      ) : null}
      <p className="text-xs text-muted-foreground">
        Delayed upstream observations and requests already in flight can move actual usage past this value before Codex LB blocks the account.
      </p>
    </section>
  );
}

function UsageLimitStateBadge({ state }: { state: AccountUsageLimitState }) {
  if (state === "reached") {
    return <Badge variant="destructive">Reached · routing blocked</Badge>;
  }
  if (state === "data_unavailable") {
    return <Badge variant="destructive">Usage unavailable · routing blocked</Badge>;
  }
  if (state === "available") {
    return <Badge variant="secondary">Active</Badge>;
  }
  return <Badge variant="outline">Off</Badge>;
}

function formatPercent(value: number): string {
  return String(Number(Math.max(0, value).toFixed(2)));
}
