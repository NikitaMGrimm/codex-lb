import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AccountUsageLimitControl } from "@/features/accounts/components/account-usage-limit-control";
import type { AccountSummary } from "@/features/accounts/schemas";
import { createAccountSummary } from "@/test/mocks/factories";

function renderControl(overrides: Partial<AccountSummary> = {}) {
  const account = createAccountSummary({
    usageLimitEnabled: true,
    usageLimitPercent: 10,
    usageLimitState: "available",
    ...overrides,
  });
  const onChange = vi.fn();
  return {
    ...render(
      <AccountUsageLimitControl account={account} busy={false} readOnly={false} onChange={onChange} />,
    ),
    user: userEvent.setup(),
    account,
    onChange,
  };
}

describe("AccountUsageLimitControl", () => {
  it("explains, toggles, edits, and removes a retained limit", async () => {
    const { user, onChange, account } = renderControl({
      usageLimitEnabled: false,
      usageLimitState: "disabled",
    });

    expect(screen.getAllByText("10% maximum used · 90% reserved")).toHaveLength(1);
    expect(screen.getAllByText("Off")).toHaveLength(1);
    expect(screen.getByRole("switch", { name: "Usage limit" })).not.toBeChecked();
    expect(screen.getByText(/in-flight requests may briefly exceed/i)).toBeInTheDocument();

    await user.click(screen.getByRole("switch", { name: "Usage limit" }));
    expect(onChange).toHaveBeenCalledWith(account.accountId, {
      enabled: true,
    });

    const input = screen.getByRole("spinbutton", { name: "Maximum used percent" });
    await user.clear(input);
    await user.type(input, "12.5");
    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(onChange).toHaveBeenCalledWith(account.accountId, {
      enabled: false,
      percent: 12.5,
    });

    await user.click(screen.getByRole("button", { name: "Clear saved limit" }));
    expect(onChange).toHaveBeenCalledWith(account.accountId, {
      enabled: false,
      percent: null,
    });
  });

  it("sets and enables a new limit", async () => {
    const { user, onChange, account } = renderControl({
      usageLimitEnabled: false,
      usageLimitPercent: null,
      usageLimitState: "disabled",
    });

    expect(screen.queryByText(/usage reporting is delayed/i)).not.toBeInTheDocument();
    await user.type(
      screen.getByRole("spinbutton", { name: "Maximum used percent" }),
      "10",
    );
    expect(screen.getByText(/usage reporting is delayed/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Set and enable" }));

    expect(onChange).toHaveBeenCalledWith(account.accountId, {
      enabled: true,
      percent: 10,
    });
  });

  it("does not save an unchanged draft via Enter and disables controls while busy", async () => {
    const { user, onChange, account, rerender } = renderControl();

    const input = screen.getByRole("spinbutton", { name: "Maximum used percent" });
    await user.type(input, "{Enter}");
    expect(onChange).not.toHaveBeenCalled();

    rerender(
      <AccountUsageLimitControl
        account={account}
        busy
        readOnly={false}
        onChange={onChange}
      />,
    );
    expect(screen.getByRole("switch", { name: "Usage limit" })).toBeDisabled();
    expect(screen.getByRole("spinbutton", { name: "Maximum used percent" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Clear saved limit" })).toBeDisabled();
  });

  it("explains invalid percentages and clears the error after correction", async () => {
    const { user } = renderControl({
      usageLimitEnabled: false,
      usageLimitPercent: null,
      usageLimitState: "disabled",
    });

    const input = screen.getByRole("spinbutton", { name: "Maximum used percent" });
    const save = screen.getByRole("button", { name: "Set and enable" });
    await user.type(input, "0");

    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Enter a percentage greater than 0 and no more than 100.",
    );
    expect(save).toBeDisabled();

    await user.clear(input);
    await user.type(input, "10");

    expect(input).toHaveAttribute("aria-invalid", "false");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(save).toBeEnabled();
  });

  it.each([
    { configured: 1e-7, edited: "0.0000002", saved: 2e-7 },
    { configured: 0.001, edited: "0.002", saved: 0.002 },
    { configured: 99.999, edited: "99.998", saved: 99.998 },
  ])(
    "preserves and saves the configured precision for $configured percent",
    async ({ configured, edited, saved }) => {
      const { user, onChange, account } = renderControl({
        usageLimitPercent: configured,
      });

      const input = screen.getByRole("spinbutton", {
        name: "Maximum used percent",
      });
      expect(input).toHaveValue(configured);
      expect(screen.getByText(new RegExp(`${configured}% maximum used`))).toBeInTheDocument();

      await user.clear(input);
      await user.type(input, edited);
      await user.click(screen.getByRole("button", { name: "Save" }));

      expect(onChange).toHaveBeenCalledWith(account.accountId, {
        enabled: true,
        percent: saved,
      });
    },
  );
});
