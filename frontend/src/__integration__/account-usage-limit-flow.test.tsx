import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import App from "@/App";
import { createAccountSummary } from "@/test/mocks/factories";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/utils";

describe("account usage limit flow", () => {
  it("shows a successful limit update when the account-list refetch fails", async () => {
    const user = userEvent.setup({ delay: null });
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
      http.put("/api/accounts/:accountId/usage-limit", async ({ params, request }) => {
        const payload = (await request.json()) as {
          enabled: boolean;
          percent?: number | null;
        };
        return HttpResponse.json({
          accountId: String(params.accountId),
          ...payload,
          percent: account.usageLimitPercent,
        });
      }),
    );

    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);

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
    const user = userEvent.setup({ delay: null });
    const staleAccount = createAccountSummary({
      accountId: "acc-stale-usage-limit",
      email: "stale-usage-limit@example.com",
      displayName: "Stale Usage Limit Account",
      usageLimitEnabled: !enabled,
      usageLimitPercent: 10,
      usageLimitState: "available",
    });
    let accountListRequests = 0;
    let storedPercent: number | null = 20;
    const updatePayloads: Array<{ enabled: boolean; percent?: number | null }> = [];

    server.use(
      http.get("/api/accounts", () => {
        accountListRequests += 1;
        return HttpResponse.json({
          accounts: [
            accountListRequests === 1
              ? staleAccount
              : {
                  ...staleAccount,
                  usageLimitEnabled: enabled,
                  usageLimitPercent: storedPercent,
                  usageLimitState: enabled ? "available" : "disabled",
                },
          ],
        });
      }),
      http.put("/api/accounts/:accountId/usage-limit", async ({ params, request }) => {
        const payload = (await request.json()) as {
          enabled: boolean;
          percent?: number | null;
        };
        updatePayloads.push(payload);
        if (payload.percent !== undefined) {
          storedPercent = payload.percent;
        }
        return HttpResponse.json({
          accountId: String(params.accountId),
          enabled: payload.enabled,
          percent: storedPercent,
        });
      }),
    );

    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);

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
    const user = userEvent.setup({ delay: null });
    const account = createAccountSummary({ usageLimitEnabled: false, usageLimitPercent: 10 });
    const updatePayloads: unknown[] = [];
    server.use(
      http.get("/api/accounts", () => HttpResponse.json({ accounts: [account] })),
      http.put("/api/accounts/:accountId/usage-limit", async ({ request }) => {
        updatePayloads.push(await request.json());
        return HttpResponse.json({
          error: {
            code: "account_usage_limit_not_configured",
            message: "Configure a percentage before enabling the usage limit",
          },
        }, { status: 409 });
      }),
    );

    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);
    const toggle = await screen.findByRole("switch", { name: "Usage limit" });
    await user.click(toggle);

    expect(await screen.findByText("Configure a percentage before enabling the usage limit")).toBeInTheDocument();
    expect(toggle).not.toBeChecked();
    expect(updatePayloads).toEqual([{ enabled: true }]);
  });
});
