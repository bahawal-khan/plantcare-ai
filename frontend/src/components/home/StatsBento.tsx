"use client";

import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import { NumberTicker } from "@/components/ui/NumberTicker";
import { LeafIcon, ShieldIcon, GaugeIcon, LayersIcon, TargetIcon } from "@/components/ui/icons";
import { datasetStats } from "@/lib/dataset-stats";
import type { CatalogStats } from "@/lib/format";

function MiniTile({
  icon,
  value,
  format,
  label,
  delay,
  className = "",
}: {
  icon: React.ReactNode;
  value: number | null;
  format?: (n: number) => string;
  label: string;
  delay: number;
  className?: string;
}) {
  return (
    <Reveal
      delay={delay}
      className={`flex flex-col items-start gap-1 rounded-2xl border border-border-default bg-surface-card p-6 shadow-sm shadow-black/5 ${className}`}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
        {icon}
      </div>
      <p className="mt-4 text-3xl font-bold text-text-strong">
        {value != null ? <NumberTicker value={value} format={format} /> : "—"}
      </p>
      <p className="text-sm text-text-muted">{label}</p>
    </Reveal>
  );
}

export function StatsBento({
  catalog,
  evaluationAccuracy,
  reachable,
}: {
  catalog: CatalogStats | null;
  evaluationAccuracy: number | null | undefined;
  reachable: boolean;
}) {
  return (
    <section className="py-4">
      <Container>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4 sm:grid-rows-2">
          <Reveal className="sm:col-span-2 sm:row-span-2 overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-ink-900 via-ink-800 to-brand-900 p-8 text-white shadow-sm shadow-black/10">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10 text-brand-300">
              <GaugeIcon className="h-6 w-6" />
            </div>
            <p className="mt-6 text-5xl font-bold tracking-tight sm:text-6xl">
              {evaluationAccuracy != null ? (
                <NumberTicker value={evaluationAccuracy * 100} format={(n) => `${n.toFixed(1)}%`} />
              ) : (
                "—"
              )}
            </p>
            <p className="mt-2 text-base font-semibold text-white/80">Evaluation Accuracy</p>
            <p className="mt-3 max-w-sm text-sm text-white/50">
              Measured on a held-out test split of {datasetStats.testImages.toLocaleString()} images across
              all {datasetStats.numClasses} trained classes &mdash; never seen during training or model
              selection.
            </p>
          </Reveal>

          <MiniTile
            icon={<LeafIcon className="h-5 w-5" />}
            value={catalog?.plantCount ?? null}
            format={(n) => `${Math.round(n)}+`}
            label="Plants Supported"
            delay={80}
            className="sm:col-start-3 sm:row-start-1"
          />
          <MiniTile
            icon={<ShieldIcon className="h-5 w-5" />}
            value={catalog?.diseaseClassCount ?? null}
            format={(n) => `${Math.round(n)}+`}
            label="Diseases Detected"
            delay={120}
            className="sm:col-start-4 sm:row-start-1"
          />
          <MiniTile
            icon={<LayersIcon className="h-5 w-5" />}
            value={datasetStats.trainImages}
            label="Training Images"
            delay={160}
            className="sm:col-start-3 sm:row-start-2"
          />
          <MiniTile
            icon={<TargetIcon className="h-5 w-5" />}
            value={datasetStats.testImages}
            label="Test Images"
            delay={200}
            className="sm:col-start-4 sm:row-start-2"
          />
        </div>
        {!reachable && (
          <p className="mt-4 text-center text-xs text-text-muted">
            Live model statistics are unavailable right now &mdash; the backend API could not be reached.
          </p>
        )}
      </Container>
    </section>
  );
}
