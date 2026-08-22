/**
 * Presentation-only helpers. These reformat strings/numbers the backend
 * already returned -- they never derive new facts, disease content, or
 * model metrics (CLAUDE.md rule 5).
 */

export function titleCase(value: string): string {
  return value
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function formatPercent(value: number, fractionDigits = 1): string {
  return `${(value * 100).toFixed(fractionDigits)}%`;
}

/** Mirrors backend/app/services/prediction_service.py::split_class_name. */
export function splitClassName(className: string): { plant: string; disease: string } {
  const [plantRaw, diseaseRaw = ""] = className.split("___");
  const plant = plantRaw.replace(/_/g, " ").trim();
  const disease = diseaseRaw.replace(/_/g, " ").trim() || "Healthy";
  return { plant, disease };
}

export interface CatalogStats {
  plantCount: number;
  diseaseClassCount: number;
  totalClassCount: number;
}

/** Derives real catalog counts from the model's supported class list -- never hard-coded. */
export function computeCatalogStats(supportedClasses: string[]): CatalogStats {
  const plants = new Set<string>();
  let diseaseClassCount = 0;

  for (const className of supportedClasses) {
    const { plant, disease } = splitClassName(className);
    plants.add(plant);
    if (disease.toLowerCase() !== "healthy") {
      diseaseClassCount += 1;
    }
  }

  return {
    plantCount: plants.size,
    diseaseClassCount,
    totalClassCount: supportedClasses.length,
  };
}

/**
 * Maps a disease record's free-text severity (as authored in
 * data/disease_info.json, e.g. "Low to Moderate", "Moderate to High") to a
 * Badge tone. Falls back to "neutral" for any value outside the known set
 * rather than guessing.
 */
export function severityTone(severity: string | undefined | null): "neutral" | "success" | "warning" | "danger" {
  if (!severity) return "neutral";
  const value = severity.toLowerCase();
  if (value === "none") return "success";
  if (value.includes("high")) return "danger";
  if (value.includes("moderate")) return "warning";
  if (value.includes("low")) return "success";
  return "neutral";
}
