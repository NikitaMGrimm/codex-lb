import { describe, expect, it } from "vitest";

import { listAccounts, updateAccountUsageLimit } from "@/features/accounts/api";

describe("default account usage-limit handler", () => {
  it("saves standalone window overrides and retains them when disabled", async () => {
    const saved = await updateAccountUsageLimit("acc_primary", {
      enabled: true,
      percent: null,
      percent5H: 70,
      percentWeekly: 60,
    });
    expect(saved).toMatchObject({
      enabled: true,
      percent: null,
      percent5H: 70,
      percentWeekly: 60,
    });

    const disabled = await updateAccountUsageLimit("acc_primary", { enabled: false });
    expect(disabled).toMatchObject({
      enabled: false,
      percent: null,
      percent5H: 70,
      percentWeekly: 60,
    });
    const accounts = await listAccounts();
    expect(accounts.accounts.find((account) => account.accountId === "acc_primary")).toMatchObject({
      usageLimitEnabled: false,
      usageLimit5HPercent: 70,
      usageLimitWeeklyPercent: 60,
    });

    const removed = await updateAccountUsageLimit("acc_primary", {
      enabled: false,
      percent: null,
      percent5H: null,
      percentWeekly: null,
    });
    expect(removed).toMatchObject({
      enabled: false,
      percent: null,
      percent5H: null,
      percentWeekly: null,
    });
  });
});
