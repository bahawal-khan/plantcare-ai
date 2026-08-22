import type { Metadata } from "next";
import { UploadIcon, LayersIcon, CpuIcon, TargetIcon, ScanIcon, GaugeIcon, FlameIcon, LeafIcon, SparklesIcon } from "@/components/ui/icons";
import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import { WorkflowDiagram, type WorkflowStep } from "@/components/shared/WorkflowDiagram";

export const metadata: Metadata = {
  title: "How It Works — PlantCare AI",
  description: "The deep learning pipeline PlantCare AI uses to detect plant diseases from a leaf image.",
};

const steps: WorkflowStep[] = [
  {
    number: "1",
    icon: <UploadIcon />,
    title: "Image Upload",
    desc: "You upload a clear image of the affected plant leaf.",
  },
  {
    number: "2",
    icon: <LayersIcon />,
    title: "Preprocessing",
    desc: "The image is resized, normalized, and prepared using the same pipeline used during training.",
  },
  {
    number: "3",
    icon: <CpuIcon />,
    title: "EfficientNetB0",
    desc: "Our model, pretrained on ImageNet and fine-tuned on plant-disease imagery, extracts important features from the image.",
  },
  {
    number: "4",
    icon: <TargetIcon />,
    title: "AI Prediction",
    desc: "The model predicts the most likely disease class with a confidence score.",
  },
  {
    number: "5",
    icon: <ScanIcon />,
    title: "Grad-CAM",
    desc: "Grad-CAM highlights the image regions that most influenced the AI's prediction.",
  },
];

const whyEfficientNet = [
  { icon: <GaugeIcon />, label: "High Accuracy" },
  { icon: <FlameIcon />, label: "Lightweight" },
  { icon: <SparklesIcon />, label: "Fast Inference" },
  { icon: <LeafIcon />, label: "Transfer Learning" },
];

export default function HowItWorksPage() {
  return (
    <Container className="max-w-6xl py-16">
      <Reveal className="text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-600/20 bg-brand-500/10 px-4 py-1.5 text-xs font-semibold text-brand-700 dark:text-brand-400">
          <ScanIcon className="h-4 w-4" /> The AI Pipeline
        </span>
        <h1 className="mt-5 text-3xl font-bold text-text-strong sm:text-4xl">How PlantCare AI Works</h1>
        <p className="mx-auto mt-3 max-w-xl text-text-body">
          Our AI system follows a deep learning pipeline to detect plant diseases accurately.
        </p>
      </Reveal>

      <div className="mt-16">
        <WorkflowDiagram steps={steps} variant="full" />
      </div>

      <Reveal className="relative mt-16 overflow-hidden rounded-2xl bg-gradient-to-br from-ink-900 via-ink-800 to-brand-900 p-8 text-white sm:p-10">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-dot-grid-on-dark" aria-hidden="true" />
        <h2 className="text-xl font-bold">Why EfficientNetB0?</h2>
        <p className="mt-2 max-w-2xl text-sm text-white/60">
          EfficientNetB0 balances accuracy and computational cost well, making it a practical
          choice for CPU-oriented deployment.
        </p>
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {whyEfficientNet.map((item, i) => (
            <Reveal
              key={item.label}
              delay={i * 70}
              className="group relative flex flex-col items-center gap-2 overflow-hidden rounded-xl bg-white/5 p-4 text-center transition-all duration-300 hover:-translate-y-1 hover:bg-white/10"
            >
              <div
                className="pointer-events-none absolute -left-6 -top-6 h-20 w-20 rounded-full bg-brand-400/0 blur-2xl transition-colors duration-500 group-hover:bg-brand-400/25"
                aria-hidden="true"
              />
              <div className="relative text-brand-400 transition-transform duration-300 group-hover:scale-110">
                {item.icon}
              </div>
              <p className="relative text-sm font-medium">{item.label}</p>
            </Reveal>
          ))}
        </div>
      </Reveal>
    </Container>
  );
}
