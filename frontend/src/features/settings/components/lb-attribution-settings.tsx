import { useState } from "react";
import { ChartPie } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import type { AccountSummary } from "@/features/accounts/schemas";
import { buildSettingsUpdateRequest } from "@/features/settings/payload";
import type { DashboardSettings, SettingsUpdateRequest } from "@/features/settings/schemas";

export function LbAttributionSettings({
  settings,
  accounts = [],
  busy,
  onSave,
}: {
  settings: DashboardSettings;
  accounts?: AccountSummary[];
  busy: boolean;
  onSave: (payload: SettingsUpdateRequest) => Promise<void>;
}) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState(settings.proWeeklyCapacityMultiplier?.toString() ?? "");
  const [references, setReferences] = useState(settings.quotaLbShareReferenceAccountIds);
  const referencesChanged = [...references].sort().join(",") !== [...settings.quotaLbShareReferenceAccountIds].sort().join(",");
  const value = Number(draft);
  const valid = draft.trim() !== "" && Number.isFinite(value) && value > 0 && value <= 1000;
  const changed = valid && value !== settings.proWeeklyCapacityMultiplier;

  return (
    <section className="rounded-xl border bg-card p-5">
      <div className="flex items-start gap-2.5">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
          <ChartPie className="h-4 w-4 text-primary" aria-hidden="true" />
        </div>
        <div className="min-w-0 space-y-1">
          <h3 className="text-sm font-semibold">{t("settings.lbAttribution.title")}</h3>
          <p className="text-xs text-muted-foreground">{t("settings.lbAttribution.description")}</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-end gap-2">
        <label className="min-w-0 flex-1 text-xs font-medium sm:max-w-48">
          {t("settings.lbAttribution.multiplier")}
          <Input
            aria-label={t("settings.lbAttribution.multiplier")}
            className="mt-1 h-8"
            type="number"
            inputMode="decimal"
            min="0.1"
            max="1000"
            step="0.1"
            placeholder={t("settings.lbAttribution.placeholder")}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            disabled={busy}
          />
        </label>
        <Button
          size="sm"
          disabled={busy || !changed}
          onClick={() => void onSave(buildSettingsUpdateRequest(settings, { proWeeklyCapacityMultiplier: value }))}
        >
          {t("settings.lbAttribution.save")}
        </Button>
        <Button
          size="sm"
          variant="outline"
          disabled={busy || settings.proWeeklyCapacityMultiplier === null}
          onClick={() => void onSave(buildSettingsUpdateRequest(settings, { proWeeklyCapacityMultiplier: null }))}
        >
          {t("settings.lbAttribution.reset")}
        </Button>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        {settings.proWeeklyCapacityMultiplier === null
          ? t("settings.lbAttribution.usingCredits")
          : t("settings.lbAttribution.current", { value: settings.proWeeklyCapacityMultiplier })}
      </p>
      <fieldset className="mt-5 space-y-2" disabled={busy}>
        <legend className="text-xs font-medium">{t("settings.lbAttribution.references")}</legend>
        <p className="text-xs text-muted-foreground">{t("settings.lbAttribution.referencesHelp")}</p>
        {accounts.map((account) => (
          <label key={account.accountId} className="flex items-center gap-2 text-xs">
            <Checkbox
              checked={references.includes(account.accountId)}
              disabled={busy}
              onCheckedChange={(checked) => setReferences((current) => checked === true
                ? [...current.filter((id) => id !== account.accountId), account.accountId]
                : current.filter((id) => id !== account.accountId))}
            />
            {account.email} ({account.planType})
          </label>
        ))}
        <Button
          size="sm"
          disabled={busy || !referencesChanged}
          onClick={() => void onSave(buildSettingsUpdateRequest(settings, { quotaLbShareReferenceAccountIds: references }))}
        >
          {t("settings.lbAttribution.saveReferences")}
        </Button>
      </fieldset>
    </section>
  );
}
