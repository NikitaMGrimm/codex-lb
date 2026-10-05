import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AccountCard } from "@/features/dashboard/components/account-card";
import { AccountList } from "@/features/dashboard/components/account-list";
import { QuotaLbShareResponseSchema } from "@/features/dashboard/schemas";
import { createAccountSummary } from "@/test/mocks/factories";

const estimate = {
  accountId: "pro-1", since: "2026-10-02T21:13:12Z", asOf: "2026-10-05T15:00:00Z",
  resetAt: "2026-10-09T21:13:12Z", windowMinutes: 10080,
  observedUsedPercent: 16, observedUsedCredits: 24192, estimatedLbUsedCredits: 48384,
  estimatedLbUsedPercent: 32, estimatedLbSharePercent: 200, referenceAccountCount: 1,
};

afterEach(() => vi.useRealTimers());

describe("current-cycle LB attribution", () => {
  it("accepts values above 100% in the API schema", () => {
    expect(QuotaLbShareResponseSchema.parse({ estimates: [estimate] }).estimates[0].estimatedLbSharePercent).toBe(200);
  });

  for (const layout of ["card", "list"] as const) {
    it(`shows uncapped estimates and dates in the ${layout} quota`, () => {
      vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-05T15:00:00Z"));
      const account = createAccountSummary({ accountId: "pro-1", planType: "pro", resetAtSecondary: estimate.resetAt });
      render(layout === "card" ? <AccountCard account={account} quotaLbShare={estimate} /> : <AccountList accounts={[account]} quotaLbShares={new Map([[account.accountId, estimate]])} />);
      expect(screen.getByTestId("quota-lb-share")).toHaveTextContent("≈200% via LB");
      expect(screen.getByTestId("quota-lb-share")).toHaveAttribute("title", expect.stringContaining("current quota cycle"));
      expect(screen.getByTestId("quota-lb-share")).toHaveAttribute("title", expect.stringContaining(new Date(estimate.since).toLocaleString()));
    });

    it(`hides a prior-cycle cached estimate after an early reset in the ${layout}`, () => {
      vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-05T15:00:00Z"));
      const account = createAccountSummary({ accountId: "pro-1", planType: "pro", resetAtSecondary: "2026-10-12T15:00:00Z" });
      render(layout === "card" ? <AccountCard account={account} quotaLbShare={estimate} /> : <AccountList accounts={[account]} quotaLbShares={new Map([[account.accountId, estimate]])} />);
      expect(screen.queryByTestId("quota-lb-share")).not.toBeInTheDocument();
      expect(screen.getByTestId("quota-lb-share-unavailable")).toBeInTheDocument();
    });

    it(`hides an expired cached estimate in the ${layout}`, () => {
      vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-10T00:00:00Z"));
      const account = createAccountSummary({ accountId: "pro-1", planType: "pro" });
      render(layout === "card" ? <AccountCard account={account} quotaLbShare={estimate} /> : <AccountList accounts={[account]} quotaLbShares={new Map([[account.accountId, estimate]])} />);
      expect(screen.queryByTestId("quota-lb-share")).not.toBeInTheDocument();
    });
  }
});

it("hides the old estimate when a zero-use reading precedes the deadline refresh", () => {
  vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-05T15:00:00Z"));
  const account = createAccountSummary({ accountId: "pro-1", planType: "pro", usage: { primaryRemainingPercent: 100, secondaryRemainingPercent: 100 }, resetAtSecondary: estimate.resetAt });
  render(<AccountCard account={account} quotaLbShare={estimate} />);
  expect(screen.queryByTestId("quota-lb-share")).not.toBeInTheDocument();
});

it("hides an early reset within one day of the previous reset", () => {
  vi.useFakeTimers(); vi.setSystemTime(new Date("2026-10-05T11:00:00Z"));
  const recent = { ...estimate, since: "2026-10-05T10:00:00Z", asOf: "2026-10-05T10:30:00Z", resetAt: "2026-10-12T10:00:00Z" };
  const account = createAccountSummary({ accountId: "pro-1", planType: "pro", resetAtSecondary: "2026-10-12T10:45:00Z" });
  render(<AccountCard account={account} quotaLbShare={recent} />);
  expect(screen.queryByTestId("quota-lb-share")).not.toBeInTheDocument();
});
