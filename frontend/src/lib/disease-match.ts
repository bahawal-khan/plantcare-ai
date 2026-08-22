import type { DiseaseRecord } from "./types";

function normalize(value: string): string {
  return value.toLowerCase().replace(/[\s_-]+/g, " ").trim();
}

/**
 * Best-effort match between a model prediction (plant + disease strings)
 * and a disease_info.json record. There is no fixed id convention between
 * class_mapping.json and disease_info.json (PROJECT_SPEC.md section 11), so
 * this only matches on plant + fuzzy name overlap -- and returns null rather
 * than guessing, since data/disease_info.json may not have every class yet.
 */
export function findMatchingDisease(
  diseases: DiseaseRecord[],
  plant: string,
  disease: string,
): DiseaseRecord | null {
  const normPlant = normalize(plant);
  const normDisease = normalize(disease);

  return (
    diseases.find((record) => {
      if (normalize(record.plant) !== normPlant) return false;
      const recordName = normalize(record.name);
      return recordName.includes(normDisease) || normDisease.includes(recordName);
    }) ?? null
  );
}
