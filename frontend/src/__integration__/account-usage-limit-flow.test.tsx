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

  it("disables from a stale tab without reverting the newer stored percentage", async () => {
    const user = userEvent.setup({ delay: null });
    const staleAccount = createAccountSummary({
      accountId: "acc-stale-usage-limit",
      email: "stale-usage-limit@example.com",
      displayName: "Stale Usage Limit Account",
      usageLimitEnabled: true,
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
                  usageLimitEnabled: false,
                  usageLimitPercent: storedPercent,
                  usageLimitState: "disabled",
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
    expect(usageLimitSwitch).toBeChecked();
    expect(screen.getByText("10% maximum used · 90% reserved")).toBeInTheDocument();

    await user.click(usageLimitSwitch);

    await waitFor(() => {
      expect(updatePayloads).toEqual([{ enabled: false }]);
      expect(screen.getByRole("switch", { name: "Usage limit" })).not.toBeChecked();
      expect(screen.getByText("20% maximum used · 80% reserved")).toBeInTheDocument();
    });
  });
});
