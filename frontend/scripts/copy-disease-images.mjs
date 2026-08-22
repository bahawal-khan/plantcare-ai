#!/usr/bin/env node
/**
 * One-off asset prep: copies one representative photo per disease class from
 * the raw PlantVillage training set into frontend/public/diseases/<id>.jpg
 * for use in the Disease Library / Disease Detail UI.
 *
 * data/class_mapping.json ("Plant___Disease" -> index) and
 * data/disease_info.json (array, index-aligned with class_mapping) are the
 * source of truth -- this script only copies files, it never edits either.
 */
import { readFileSync, existsSync, mkdirSync, copyFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");

const classMappingPath = path.join(repoRoot, "data", "class_mapping.json");
const diseaseInfoPath = path.join(repoRoot, "data", "disease_info.json");
const rawImagesDir = path.join(repoRoot, "data", "raw", "plantvillage", "raw", "color");
const outDir = path.join(__dirname, "..", "public", "diseases");

const classMapping = JSON.parse(readFileSync(classMappingPath, "utf-8"));
const diseaseInfo = JSON.parse(readFileSync(diseaseInfoPath, "utf-8"));

mkdirSync(outDir, { recursive: true });

const byIndex = Object.entries(classMapping).sort((a, b) => a[1] - b[1]);

let copied = 0;
let skipped = 0;

for (const [className, index] of byIndex) {
  const record = diseaseInfo[index];
  if (!record?.id) {
    console.warn(`No disease_info record for index ${index} (${className}) -- skipping`);
    skipped++;
    continue;
  }

  const classDir = path.join(rawImagesDir, className);
  if (!existsSync(classDir)) {
    console.warn(`Missing raw image directory for "${className}" -- skipping ${record.id}`);
    skipped++;
    continue;
  }

  const files = readdirSync(classDir)
    .filter((f) => /\.(jpe?g|png)$/i.test(f))
    .sort();
  if (files.length === 0) {
    console.warn(`No images found in ${classDir} -- skipping ${record.id}`);
    skipped++;
    continue;
  }

  // Deterministic pick from the middle of the sorted list rather than always
  // the first file, so we're not systematically biased toward one filename pattern.
  const chosen = files[Math.floor(files.length / 2)];
  copyFileSync(path.join(classDir, chosen), path.join(outDir, `${record.id}.jpg`));
  copied++;
}

console.log(`Copied ${copied} disease images to ${path.relative(repoRoot, outDir)} (${skipped} skipped).`);
