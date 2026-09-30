import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { LbAttributionSettings } from "@/features/settings/components/lb-attribution-settings";
import { createDashboardSettings } from "@/test/mocks/factories";

describe("LbAttributionSettings", () => {
  it("saves a valid Pro ratio and can reset to subscription credits", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    const settings = createDashboardSettings({ proWeeklyCapacityMultiplier: null });
    const { rerender } = render(<LbAttributionSettings settings={settings} busy={false} onSave={onSave} />);

    const input = screen.getByRole("spinbutton", { name: "Pro / Plus weekly ratio" });
    await user.type(input, "20");
    await user.click(screen.getByRole("button", { name: "Save ratio" }));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ proWeeklyCapacityMultiplier: 20 }));

    rerender(<LbAttributionSettings key="20" settings={{ ...settings, proWeeklyCapacityMultiplier: 20 }} busy={false} onSave={onSave} />);
    await user.click(screen.getByRole("button", { name: "Use credits" }));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ proWeeklyCapacityMultiplier: null }));
  });

  it("does not save an invalid ratio", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(<LbAttributionSettings settings={createDashboardSettings()} busy={false} onSave={onSave} />);
    await user.type(screen.getByRole("spinbutton", { name: "Pro / Plus weekly ratio" }), "0");
    expect(screen.getByRole("button", { name: "Save ratio" })).toBeDisabled();
    expect(onSave).not.toHaveBeenCalled();
  });
});
