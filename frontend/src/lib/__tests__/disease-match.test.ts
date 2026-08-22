import { describe, expect, it } from "vitest";
import { findMatchingDisease } from "../disease-match";
import type { DiseaseRecord } from "../types";

const diseases: DiseaseRecord[] = [
  { id: "tomato-early-blight", plant: "Tomato", name: "Early Blight" },
  { id: "apple-scab", plant: "Apple", name: "Apple Scab" },
];

describe("findMatchingDisease", () => {
  it("matches on plant + fuzzy disease name overlap", () => {
    const match = findMatchingDisease(diseases, "Tomato", "Early blight");
    expect(match?.id).toBe("tomato-early-blight");
  });

  it("is case/underscore/hyphen insensitive", () => {
    const match = findMatchingDisease(diseases, "apple", "scab");
    expect(match?.id).toBe("apple-scab");
  });

  it("returns null instead of guessing when there is no match", () => {
    const match = findMatchingDisease(diseases, "Grape", "Black rot");
    expect(match).toBeNull();
  });

  it("returns null for an empty disease list", () => {
    expect(findMatchingDisease([], "Tomato", "Early blight")).toBeNull();
  });
});
