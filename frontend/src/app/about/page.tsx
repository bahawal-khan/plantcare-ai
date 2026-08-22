import type { Metadata } from "next";
import { getModelInfoSafe } from "@/lib/api";
import { computeCatalogStats } from "@/lib/format";
import { datasetStats } from "@/lib/dataset-stats";
import { StatTile } from "@/components/ui/StatTile";
import { AnimatedStatTile } from "@/components/ui/AnimatedStatTile";
import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import { LeafIcon, ShieldIcon, GaugeIcon, CpuIcon, ScanIcon, SparklesIcon } from "@/components/ui/icons";

export const metadata: Metadata = {
  title: "About — PlantCare AI",
  description: "About PlantCare AI, an AI-powered plant disease detection platform.",
};

const pillars = [
  {
    icon: <ShieldIcon className="h-6 w-6" />,
    title: "Our Mission",
    desc: "Make plant disease detection accessible to everyone using AI.",
  },
  {
    icon: <LeafIcon className="h-6 w-6" />,
    title: "Our Vision",
    desc: "A world where every plant is healthy and disease-free.",
  },
  {
    icon: <CpuIcon className="h-6 w-6" />,
    title: "Our Technology",
    desc: "We use a transfer-learned EfficientNetB0 deep learning model with Grad-CAM explainability for transparent, AI-assisted diagnosis.",
  },
  {
    icon: <ScanIcon className="h-6 w-6" />,
    title: "Responsible AI",
    desc: "Every prediction ships with a confidence score and a Grad-CAM explanation of what the model attended to. Results are decision support, not a replacement for expert agronomic or plant-pathology diagnosis.",
  },
];

export default async function AboutPage() {
  const modelInfo = await getModelInfoSafe();
  const catalog = modelInfo ? computeCatalogStats(modelInfo.supported_classes) : null;

  return (
    <Container className="max-w-6xl py-16">
      <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
        <Reveal>
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-600/20 bg-brand-500/10 px-4 py-1.5 text-xs font-semibold text-brand-700 dark:text-brand-400">
            <SparklesIcon className="h-4 w-4" /> About PlantCare AI
          </span>
          <h1 className="mt-5 text-3xl font-bold text-text-strong sm:text-4xl">About PlantCare AI</h1>
          <p className="mt-4 text-text-body">
            PlantCare AI is a deep learning platform designed to help farmers, gardeners, and
            plant enthusiasts identify plant diseases early and take the right action.
          </p>

          <div className="mt-8 space-y-4">
            {pillars.map((pillar, i) => (
              <Reveal
                key={pillar.title}
                delay={i * 80}
                className="group relative flex gap-4 overflow-hidden rounded-2xl border border-border-default bg-surface-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/5"
              >
                <div
                  className="pointer-events-none absolute -left-8 -top-8 h-24 w-24 rounded-full bg-brand-500/0 blur-2xl transition-colors duration-500 group-hover:bg-brand-500/20"
                  aria-hidden="true"
                />
                <div className="relative mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-500/10 text-brand-600 transition-transform duration-300 group-hover:scale-110 dark:text-brand-400">
                  {pillar.icon}
                </div>
                <div className="relative">
                  <p className="font-semibold text-text-strong">{pillar.title}</p>
                  <p className="mt-1 text-sm text-text-body">{pillar.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </Reveal>

        <Reveal className="relative mx-auto flex aspect-square w-full max-w-sm items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-brand-200/70 to-brand-50/40 blur-2xl dark:from-brand-800/30 dark:to-brand-900/10" />
          <div
            className="absolute inset-4 animate-[spin_24s_linear_infinite] rounded-full border border-dashed border-brand-400/40 dark:border-brand-500/25"
            aria-hidden="true"
          />
          <div className="relative flex h-[85%] w-[85%] items-center justify-center rounded-full border border-border-default bg-surface-card/80 shadow-xl shadow-black/10 backdrop-blur-sm">
            <svg viewBox="0 0 200 200" className="h-40 w-40" aria-hidden="true">
              <defs>
                <linearGradient id="aboutLeafGradient" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#4ade80" />
                  <stop offset="100%" stopColor="#0f7a3a" />
                </linearGradient>
              </defs>
              <path
                d="M100 178c48-8 74-46 74-108C104 70 34 96 26 170c22-46 52-76 104-92-32 26-52 60-30 100Z"
                fill="url(#aboutLeafGradient)"
              />
              <path
                d="M30 168c10-40 36-70 78-88"
                fill="none"
                stroke="rgba(255,255,255,0.55)"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
        </Reveal>
      </div>

      <div className="mt-16 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {catalog ? (
          <AnimatedStatTile icon={<LeafIcon />} value={catalog.plantCount} kind="plus" label="Plants Supported" />
        ) : (
          <StatTile icon={<LeafIcon />} value="—" label="Plants Supported" />
        )}
        {catalog ? (
          <AnimatedStatTile
            icon={<ShieldIcon />}
            value={catalog.diseaseClassCount}
            kind="plus"
            label="Diseases Detected"
          />
        ) : (
          <StatTile icon={<ShieldIcon />} value="—" label="Diseases Detected" />
        )}
        {modelInfo?.evaluation_accuracy != null ? (
          <AnimatedStatTile
            icon={<GaugeIcon />}
            value={modelInfo.evaluation_accuracy * 100}
            kind="percent"
            label="Evaluation Accuracy"
          />
        ) : (
          <StatTile icon={<GaugeIcon />} value="—" label="Evaluation Accuracy" />
        )}
        <StatTile icon={<CpuIcon />} value={modelInfo?.model_name ?? "—"} label="Model Architecture" />
      </div>
      {!modelInfo && (
        <p className="mt-4 text-center text-xs text-text-muted">
          Live model statistics are unavailable right now &mdash; the backend API could not be reached.
        </p>
      )}

      <Reveal className="mt-4 text-center text-xs text-text-muted">
        Trained on {datasetStats.trainImages.toLocaleString()} images and evaluated on a held-out test
        split of {datasetStats.testImages.toLocaleString()} images, spanning all {datasetStats.numClasses}{" "}
        supported plant/disease classes.
      </Reveal>
    </Container>
  );
}
