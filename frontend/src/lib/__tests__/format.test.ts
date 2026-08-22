import { describe, expect, it } from "vitest";
import { computeCatalogStats, formatPercent, splitClassName, titleCase } from "../format";

describe("titleCase", () => {
  it("capitalizes each word", () => {
    expect(titleCase("early blight")).toBe("Early Blight");
    expect(titleCase("healthy")).toBe("Healthy");
  });
});

describe("formatPercent", () => {
  it("formats a 0..1 confidence as a percentage string", () => {
    expect(formatPercent(0.947)).toBe("94.7%");
    expect(formatPercent(1)).toBe("100.0%");
  });
});

describe("splitClassName", () => {
  it("mirrors the backend's Plant___Disease split", () => {
    expect(splitClassName("Tomato___Early_blight")).toEqual({ plant: "Tomato", disease: "Early blight" });
    // Matches backend/app/services/prediction_service.py exactly: the "Healthy"
    // fallback only applies when there's no disease segment at all, so a
    // literal "healthy" class label stays lowercase here (titleCase() handles
    // display casing separately).
    expect(splitClassName("Apple___healthy")).toEqual({ plant: "Apple", disease: "healthy" });
  });
});

describe("computeCatalogStats", () => {
  it("derives real plant/disease counts from the supported class list only", () => {
    const stats = computeCatalogStats([
      "Apple___Apple_scab",
      "Apple___healthy",
      "Tomato___Early_blight",
      "Tomato___Late_blight",
      "Tomato___healthy",
    ]);
    expect(stats.plantCount).toBe(2);
    expect(stats.diseaseClassCount).toBe(3);
    expect(stats.totalClassCount).toBe(5);
  });

  it("returns zero counts for an empty list rather than inventing numbers", () => {
    expect(computeCatalogStats([])).toEqual({ plantCount: 0, diseaseClassCount: 0, totalClassCount: 0 });
  });
});
