"use client";

import { useMemo, useState } from "react";
import type { DiseaseRecord } from "@/lib/types";
import { SearchIcon } from "@/components/ui/icons";
import { Reveal } from "@/components/ui/Reveal";
import { DiseaseCard } from "./DiseaseCard";

export function DiseaseGrid({ diseases }: { diseases: DiseaseRecord[] }) {
  const [search, setSearch] = useState("");
  const [plantFilter, setPlantFilter] = useState("all");

  const plants = useMemo(
    () => Array.from(new Set(diseases.map((d) => d.plant))).sort(),
    [diseases],
  );

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return diseases.filter((d) => {
      const matchesPlant = plantFilter === "all" || d.plant === plantFilter;
      const matchesSearch =
        query.length === 0 ||
        d.name.toLowerCase().includes(query) ||
        d.plant.toLowerCase().includes(query);
      return matchesPlant && matchesSearch;
    });
  }, [diseases, search, plantFilter]);

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative w-full sm:max-w-xs">
          <SearchIcon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search diseases..."
            className="w-full rounded-xl border border-border-default bg-surface-card py-2.5 pl-10 pr-4 text-sm text-text-strong placeholder:text-text-muted focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>
        <select
          value={plantFilter}
          onChange={(e) => setPlantFilter(e.target.value)}
          className="rounded-xl border border-border-default bg-surface-card px-4 py-2.5 text-sm text-text-strong focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        >
          <option value="all">All Plants</option>
          {plants.map((plant) => (
            <option key={plant} value={plant}>
              {plant}
            </option>
          ))}
        </select>
      </div>

      {diseases.length === 0 ? (
        <p className="mt-12 rounded-xl border border-border-default bg-surface-inset p-8 text-center text-sm text-text-muted">
          The disease library is empty right now. Check back soon, or try the{" "}
          <a href="/diagnose" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
            Diagnose
          </a>{" "}
          flow to see live predictions.
        </p>
      ) : filtered.length === 0 ? (
        <p className="mt-12 rounded-xl border border-border-default bg-surface-inset p-8 text-center text-sm text-text-muted">
          No diseases match your search.
        </p>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {filtered.map((disease, i) => (
            <Reveal key={disease.id} delay={Math.min(i, 8) * 40}>
              <DiseaseCard disease={disease} />
            </Reveal>
          ))}
        </div>
      )}
    </div>
  );
}
