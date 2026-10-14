import { describe, expect, it } from "vitest";
import { formatCitationLabel } from "./citations.js";

describe("formatCitationLabel", () => {
  it("prefers a heading", () => {
    expect(
      formatCitationLabel({
        marker: 1,
        title: "Membership",
        heading: "Late fee",
      }),
    ).toBe("[1] Membership — Late fee");
  });

  it("falls back to a page", () => {
    expect(
      formatCitationLabel({ marker: 2, title: "Shelf", heading: "", page: 4 }),
    ).toBe("[2] Shelf — p. 4");
  });
});
