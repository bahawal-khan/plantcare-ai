import { getDiseasesSafe, getModelInfoSafe } from "@/lib/api";
import { computeCatalogStats } from "@/lib/format";
import { LinkButton, ScanRingCTA } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import { UploadIcon, CpuIcon, TargetIcon, ArrowRightIcon, LeafIcon } from "@/components/ui/icons";
import { Hero } from "@/components/home/Hero";
import { StatsBento } from "@/components/home/StatsBento";
import { FeatureBento } from "@/components/home/FeatureBento";
import { WorkflowDiagram, type WorkflowStep } from "@/components/shared/WorkflowDiagram";
import { DiseaseCard } from "@/components/diseases/DiseaseCard";

const teaserSteps: WorkflowStep[] = [
  { number: "1", icon: <UploadIcon />, title: "Upload Image", desc: "Upload a clear image of the affected leaf." },
  { number: "2", icon: <CpuIcon />, title: "AI Analysis", desc: "Our AI model analyzes the image deeply." },
  { number: "3", icon: <TargetIcon />, title: "Get Results", desc: "Receive diagnosis and treatment advice." },
];

export default async function HomePage() {
  const [modelInfo, diseases] = await Promise.all([getModelInfoSafe(), getDiseasesSafe()]);
  const catalog = modelInfo ? computeCatalogStats(modelInfo.supported_classes) : null;
  const previewDiseases = diseases.slice(0, 4);

  return (
    <div>
      <Hero />

      <StatsBento
        catalog={catalog}
        evaluationAccuracy={modelInfo?.evaluation_accuracy}
        reachable={Boolean(modelInfo)}
      />

      <FeatureBento />

      <section className="border-t border-border-default bg-surface-card py-16">
        <Container>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-text-strong sm:text-3xl">How PlantCare AI Works</h2>
            <p className="mt-2 text-text-body">Simple steps for accurate diagnosis</p>
          </div>

          <div className="mt-12">
            <WorkflowDiagram steps={teaserSteps} variant="compact" />
          </div>

          <Reveal className="mt-10 text-center">
            <LinkButton href="/how-it-works" variant="ghost" className="text-brand-700 dark:text-brand-400">
              See the full pipeline <ArrowRightIcon />
            </LinkButton>
          </Reveal>
        </Container>
      </section>

      {previewDiseases.length > 0 && (
        <section className="py-16">
          <Container>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-text-strong sm:text-3xl">Disease Library</h2>
                <p className="mt-2 text-text-body">A preview of the diseases PlantCare AI can detect</p>
              </div>
              <LinkButton href="/diseases" variant="ghost" className="text-brand-700 dark:text-brand-400">
                View All Diseases <ArrowRightIcon />
              </LinkButton>
            </div>

            <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {previewDiseases.map((disease, i) => (
                <Reveal key={disease.id} delay={i * 60}>
                  <DiseaseCard disease={disease} />
                </Reveal>
              ))}
            </div>
          </Container>
        </section>
      )}

      <section className="py-16">
        <Container>
          <Reveal className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-ink-900 via-ink-800 to-brand-900 px-6 py-14 text-center text-white sm:px-10">
            <div className="pointer-events-none absolute inset-0 -z-20 bg-dot-grid-on-dark" aria-hidden="true" />
            <div
              className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_60%_at_20%_0%,rgba(74,222,128,0.18),transparent),radial-gradient(50%_50%_at_90%_100%,rgba(74,222,128,0.12),transparent)]"
              aria-hidden="true"
            />
            <LeafIcon className="mx-auto h-10 w-10 text-brand-300" />
            <h2 className="mt-5 text-2xl font-bold sm:text-3xl">Ready to Diagnose Your Plant?</h2>
            <p className="mx-auto mt-3 max-w-xl text-white/60">
              Upload a leaf photo and get an instant AI diagnosis, backed by a transparent
              Grad-CAM explanation &mdash; free, in seconds.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <ScanRingCTA href="/diagnose">
                <LeafIcon className="h-4 w-4" /> Diagnose My Plant
              </ScanRingCTA>
              <LinkButton
                href="/diseases"
                variant="secondary"
                size="lg"
                className="border-white/20 bg-white/5 text-white hover:border-white/40 hover:text-white"
              >
                Explore Diseases
              </LinkButton>
            </div>
          </Reveal>
        </Container>
      </section>
    </div>
  );
}
