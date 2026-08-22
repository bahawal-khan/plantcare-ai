import type { DiseaseRecord } from "@/lib/types";

function toList(value: string | string[] | null | undefined): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function InfoColumn({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="rounded-xl border border-border-default bg-surface-card p-4">
      <p className="text-sm font-semibold text-brand-700 dark:text-brand-400">{title}</p>
      <ul className="mt-2 space-y-1.5 text-sm text-text-body">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-brand-500" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function DiseaseInfoSections({ disease }: { disease: DiseaseRecord }) {
  const symptoms = toList(disease.symptoms);
  const causes = toList(disease.causes);
  const prevention = toList(disease.prevention);
  const management = toList(disease.management);

  if (!symptoms.length && !causes.length && !prevention.length && !management.length) {
    return null;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <InfoColumn title="Symptoms" items={symptoms} />
      <InfoColumn title="Causes" items={causes} />
      <InfoColumn title="Prevention" items={prevention} />
      <InfoColumn title="Management" items={management} />
    </div>
  );
}
