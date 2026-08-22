import Link from "next/link";
import type { DiseaseRecord } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { severityTone } from "@/lib/format";
import { ArrowRightIcon } from "@/components/ui/icons";
import { DiseaseImage } from "./DiseaseImage";

export function DiseaseCard({ disease }: { disease: DiseaseRecord }) {
  return (
    <Link
      href={`/diseases/${encodeURIComponent(disease.id)}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-border-default bg-surface-card shadow-sm shadow-black/5 transition-all hover:-translate-y-1 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/10"
    >
      <div className="relative h-36 overflow-hidden bg-gradient-to-br from-brand-500/10 to-brand-600/15">
        <DiseaseImage
          id={disease.id}
          name={disease.name}
          plant={disease.plant}
          sizes="(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 100vw"
          imageClassName="transition-transform duration-300 group-hover:scale-105"
        />
        <div
          className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink-900/70 via-ink-900/0 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          aria-hidden="true"
        />
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center justify-between gap-2">
          <p className="font-semibold text-text-strong transition-transform duration-300 group-hover:translate-x-0.5">
            {disease.name}
          </p>
          <ArrowRightIcon className="h-4 w-4 shrink-0 -translate-x-2 text-brand-600 opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100 dark:text-brand-400" />
        </div>
        <p className="text-sm text-text-muted">{disease.plant}</p>
        {disease.severity && <Badge tone={severityTone(disease.severity)}>{disease.severity}</Badge>}
      </div>
    </Link>
  );
}
