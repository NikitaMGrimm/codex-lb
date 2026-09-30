import { useTranslation } from "react-i18next";

import type { QuotaLbShareEstimate } from "@/features/dashboard/schemas";

export function QuotaLbShareIndicator({ estimate }: { estimate: QuotaLbShareEstimate }) {
  const { t } = useTranslation();
  const label = t("dashboard.lbShare.label", { percent: Math.round(estimate.estimatedLbSharePercent) });
  return (
    <span
      className="inline-flex max-w-full items-center truncate rounded-md border border-primary/20 bg-primary/5 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-primary"
      title={t("dashboard.lbShare.explainer")}
      aria-label={`${label}. ${t("dashboard.lbShare.explainer")}`}
      data-testid="quota-lb-share"
    >
      {label}
    </span>
  );
}
