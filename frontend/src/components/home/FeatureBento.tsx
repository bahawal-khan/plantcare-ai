import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import {
  LeafIcon,
  TargetIcon,
  ScanIcon,
  LayersIcon,
  CpuIcon,
  BoltIcon,
} from "@/components/ui/icons";

const features = [
  {
    icon: <LeafIcon className="h-6 w-6" />,
    title: "AI Plant Diagnosis",
    desc: "Upload a leaf photo and get an instant plant + disease prediction from a deep learning model trained on real disease imagery.",
    span: "lg:col-span-2",
  },
  {
    icon: <TargetIcon className="h-6 w-6" />,
    title: "Confidence & Top-K",
    desc: "Every result ships with a confidence score and the next most likely alternatives, not just a single guess.",
    span: "",
  },
  {
    icon: <ScanIcon className="h-6 w-6" />,
    title: "Grad-CAM Explainability",
    desc: "See exactly which regions of the leaf influenced the prediction, rendered as a heatmap overlay on your own image.",
    span: "",
  },
  {
    icon: <LayersIcon className="h-6 w-6" />,
    title: "3D Visualization",
    desc: "Explore the Grad-CAM attention map as an interactive 3D surface you can rotate and inspect.",
    span: "",
  },
  {
    icon: <CpuIcon className="h-6 w-6" />,
    title: "EfficientNetB0",
    desc: "A transfer-learned EfficientNetB0 backbone balances accuracy with CPU-friendly inference speed.",
    span: "",
  },
  {
    icon: <BoltIcon className="h-6 w-6" />,
    title: "Fast Analysis",
    desc: "Predictions and explainability visuals are generated in a single request — no waiting on a queue.",
    span: "lg:col-span-2",
  },
];

export function FeatureBento() {
  return (
    <section className="py-16">
      <Container>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-text-strong sm:text-3xl">Built for Trustworthy AI Diagnosis</h2>
          <p className="mx-auto mt-2 max-w-xl text-text-body">
            Every prediction comes with the context you need to trust &mdash; or question &mdash; the result.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <Reveal
              key={feature.title}
              delay={i * 60}
              className={`group relative overflow-hidden rounded-2xl border border-border-default bg-surface-card p-6 transition-all hover:-translate-y-1 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/5 ${feature.span}`}
            >
              <div
                className="pointer-events-none absolute -left-10 -top-10 h-32 w-32 rounded-full bg-brand-500/0 blur-2xl transition-colors duration-500 group-hover:bg-brand-500/20"
                aria-hidden="true"
              />
              <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-brand-500/10 text-brand-600 transition-transform group-hover:scale-110 dark:text-brand-400">
                {feature.icon}
              </div>
              <p className="relative mt-4 font-semibold text-text-strong">{feature.title}</p>
              <p className="relative mt-1.5 text-sm leading-relaxed text-text-muted">{feature.desc}</p>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}
