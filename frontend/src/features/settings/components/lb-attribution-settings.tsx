import { useState } from "react";
import { ChartPie } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { buildSettingsUpdateRequest } from "@/features/settings/payload";
import type { DashboardSettings, SettingsUpdateRequest } from "@/features/settings/schemas";

export function LbAttributionSettings({
  settings,
  busy,
  onSave,
}: {
  settings: DashboardSettings;
  busy: boolean;
  onSave: (payload: SettingsUpdateRequest) => Promise<void>;
}) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState(settings.proWeeklyCapacityMultiplier?.toString() ?? "");
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
    </section>
  );
}
