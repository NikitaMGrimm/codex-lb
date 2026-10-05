import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import type { QuotaLbShareEstimate } from "@/features/dashboard/schemas";

export function QuotaLbShareIndicator({ estimate, resetAt, remainingPercent }: { estimate?: QuotaLbShareEstimate; resetAt?: string | null; remainingPercent?: number | null }) {
  const { t } = useTranslation();
  const [now, setNow] = useState(() => Date.now());
  const estimateDeadline = estimate?.resetAt ? Date.parse(estimate.resetAt) : null;
  useEffect(() => {
    if (estimateDeadline === null || estimateDeadline <= now) return;
    const timer = window.setTimeout(() => setNow(Date.now()), Math.min(Math.max(1, estimateDeadline - Date.now() + 1), 2_147_483_647));
    return () => window.clearTimeout(timer);
  }, [estimateDeadline, now]);
  const quotaDeadline = resetAt ? Date.parse(resetAt) : null;
  const expired = (remainingPercent === 100 && estimate && estimate.observedUsedPercent > 0) || (estimateDeadline !== null && (
    estimateDeadline <= now ||
    (quotaDeadline !== null && estimate && quotaDeadline > estimateDeadline && (
      quotaDeadline > estimateDeadline + 86_400_000 ||
      quotaDeadline - estimate.windowMinutes * 60_000 >= Date.parse(estimate.asOf)
    ))
  ));
  if (!estimate || expired) {
    const label = t("dashboard.lbShare.unavailable");
    const explanation = t("dashboard.lbShare.unavailableExplainer");
    return (
      <span
        className="inline-flex max-w-full items-center truncate rounded-md border border-border px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground"
        title={explanation}
        aria-label={`${label}. ${explanation}`}
        data-testid="quota-lb-share-unavailable"
      >
        {label}
      </span>
    );
  }
  const label = t("dashboard.lbShare.label", { percent: Math.round(estimate.estimatedLbSharePercent) });
  const explanation = t("dashboard.lbShare.explainer", {
    since: new Date(estimate.since).toLocaleString(),
    asOf: new Date(estimate.asOf).toLocaleString(),
  });
  return (
    <span
      className="inline-flex max-w-full items-center truncate rounded-md border border-primary/20 bg-primary/5 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-primary"
      title={explanation}
      aria-label={`${label}. ${explanation}`}
      data-testid="quota-lb-share"
    >
      {label}
    </span>
  );
}
