import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it, vi } from "vitest";

import App from "@/App";
import type { AccountSummary } from "@/features/accounts/schemas";
import { createAccountSummary } from "@/test/mocks/factories";
import * as factories from "@/test/mocks/factories";
import { resetMockState } from "@/test/mocks/handlers";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/utils";

function renderAccounts(account: AccountSummary) {
  const defaults = vi.spyOn(factories, "createDefaultAccounts").mockReturnValue([account]);
  try {
    resetMockState();
  } finally {
    defaults.mockRestore();
  }
  window.history.pushState({}, "", "/accounts");
  renderWithProviders(<App />);
  return userEvent.setup({ delay: null });
}

describe("account usage limit flow", () => {
  it.each([
    {
      usage: { primaryRemainingPercent: 82, secondaryRemainingPercent: 67 },
      expected: "Reached · routing blocked",
    },
    { usage: null, expected: "Usage unavailable · routing blocked" },
  ])("shows $expected after saving and re-enabling with the shared mock", async ({ usage, expected }) => {
    const user = renderAccounts(createAccountSummary({ usage }));
    await user.type(await screen.findByRole("spinbutton", { name: "Maximum used percent" }), "10");
    await user.click(screen.getByRole("button", { name: "Set and enable" }));
    expect(await screen.findByText(expected)).toBeInTheDocument();

    await user.click(screen.getByRole("switch", { name: "Usage limit" }));
    await waitFor(() => {
      expect(screen.getByRole("switch", { name: "Usage limit" })).not.toBeChecked();
      expect(screen.queryByText(expected)).not.toBeInTheDocument();
    });
    await user.click(screen.getByRole("switch", { name: "Usage limit" }));
    expect(await screen.findByText(expected)).toBeInTheDocument();
  });

  it("shows a successful limit update when the account-list refetch fails", async () => {
    const account = createAccountSummary({
      accountId: "acc-usage-limit",
      email: "usage-limit@example.com",
      displayName: "Usage Limit Account",
      usageLimitEnabled: false,
      usageLimitPercent: 10,
      usageLimitState: "disabled",
    });
    let accountListRequests = 0;

    server.use(
      http.get("/api/accounts", () => {
        accountListRequests += 1;
        if (accountListRequests === 1) {
          return HttpResponse.json({ accounts: [account] });
        }
        return HttpResponse.json(
          {
            error: {
              code: "forced_accounts_outage",
              message: "Forced account-list outage",
            },
          },
          { status: 500 },
        );
      }),
    );

    const user = renderAccounts(account);

    const usageLimitSwitch = await screen.findByRole("switch", {
      name: "Usage limit",
    });
    expect(usageLimitSwitch).not.toBeChecked();

    await user.click(usageLimitSwitch);

    await waitFor(() => {
      expect(accountListRequests).toBeGreaterThanOrEqual(2);
      expect(usageLimitSwitch).toBeChecked();
      expect(screen.getByText("Forced account-list outage")).toBeInTheDocument();
    });
  });

  it.each([false, true])("toggles from a stale tab with enabled=%s without reverting the newer stored percentage", async (enabled) => {
    const storedAccount = createAccountSummary({
      accountId: "acc-stale-usage-limit",
      email: "stale-usage-limit@example.com",
      displayName: "Stale Usage Limit Account",
      usageLimitEnabled: !enabled,
      usageLimitPercent: 20,
      usageLimitState: enabled ? "disabled" : "available",
      usage: { primaryRemainingPercent: 99, secondaryRemainingPercent: 99 },
    });
    let accountListRequests = 0;
    const updatePayloads: unknown[] = [];

    server.use(
      http.get("/api/accounts", () => {
        accountListRequests += 1;
        return HttpResponse.json({
          accounts: [
            accountListRequests === 1
              ? { ...storedAccount, usageLimitPercent: 10 }
              : storedAccount,
          ],
        });
      }),
      http.put("/api/accounts/:accountId/usage-limit", async ({ request }) => {
        // Record the request, then let the shared handler apply it to storedAccount.
        updatePayloads.push(await request.clone().json());
      }),
    );

    const user = renderAccounts(storedAccount);

    const usageLimitSwitch = await screen.findByRole("switch", {
      name: "Usage limit",
    });
    expect(usageLimitSwitch).toHaveAttribute("aria-checked", String(!enabled));
    expect(screen.getByText("10% maximum used · 90% reserved")).toBeInTheDocument();

    await user.click(usageLimitSwitch);

    await waitFor(() => {
      expect(updatePayloads).toEqual([{ enabled }]);
      expect(screen.getByRole("switch", { name: "Usage limit" })).toHaveAttribute("aria-checked", String(enabled));
      expect(screen.getByText("20% maximum used · 80% reserved")).toBeInTheDocument();
    });
  });

  it("shows a conflict when a stale tab enables a removed policy", async () => {
    const account = createAccountSummary({ usageLimitEnabled: false, usageLimitPercent: null });
    const updatePayloads: unknown[] = [];
    server.use(
      http.get("/api/accounts", () => HttpResponse.json({ accounts: [{ ...account, usageLimitPercent: 10 }] })),
      http.put("/api/accounts/:accountId/usage-limit", async ({ request }) => {
        updatePayloads.push(await request.clone().json());
      }),
    );

    const user = renderAccounts(account);
    const toggle = await screen.findByRole("switch", { name: "Usage limit" });
    await user.click(toggle);

    expect(await screen.findByText("Configure a percentage before enabling the usage limit")).toBeInTheDocument();
    expect(toggle).not.toBeChecked();
    expect(updatePayloads).toEqual([{ enabled: true }]);
  });
});
