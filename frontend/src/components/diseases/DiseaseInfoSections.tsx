import type { DiseaseRecord } from "@/lib/types";
import { Reveal } from "@/components/ui/Reveal";

function toList(value: string | string[] | null | undefined): string[] {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function InfoColumn({ title, items, delay }: { title: string; items: string[]; delay: number }) {
  if (items.length === 0) return null;
  return (
    <Reveal
      delay={delay}
      className="rounded-xl border border-border-default bg-surface-card p-4 transition-all duration-300 hover:-translate-y-1 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/10"
    >
      <p className="text-sm font-semibold text-brand-700 dark:text-brand-400">{title}</p>
      <ul className="mt-2 space-y-1.5 text-sm text-text-body">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-brand-500" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </Reveal>
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
      <InfoColumn title="Symptoms" items={symptoms} delay={0} />
      <InfoColumn title="Causes" items={causes} delay={60} />
      <InfoColumn title="Prevention" items={prevention} delay={120} />
      <InfoColumn title="Management" items={management} delay={180} />
    </div>
  );
}
