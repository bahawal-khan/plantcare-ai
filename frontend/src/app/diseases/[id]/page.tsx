import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ApiError, getDisease, getDiseasesSafe } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { LinkButton } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";
import { ResponsibleUseDisclaimer } from "@/components/ui/Disclaimer";
import { DiseaseInfoSections } from "@/components/diseases/DiseaseInfoSections";
import { DiseaseImage } from "@/components/diseases/DiseaseImage";
import { DiseaseCard } from "@/components/diseases/DiseaseCard";
import { LeafIcon } from "@/components/ui/icons";
import { severityTone } from "@/lib/format";

export const dynamic = "force-dynamic";

async function loadDisease(id: string) {
  try {
    return await getDisease(id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound();
    }
    return { unavailable: true as const };
  }
}

export async function generateMetadata(props: PageProps<"/diseases/[id]">): Promise<Metadata> {
  const { id } = await props.params;
  const disease = await loadDisease(id);
  if ("unavailable" in disease) {
    return { title: "Disease Detail — PlantCare AI" };
  }
  return { title: `${disease.name} — PlantCare AI` };
}

export default async function DiseaseDetailPage(props: PageProps<"/diseases/[id]">) {
  const { id } = await props.params;
  const [disease, allDiseases] = await Promise.all([loadDisease(id), getDiseasesSafe()]);

  if ("unavailable" in disease) {
    return (
      <Container className="max-w-3xl py-16 text-center">
        <p className="font-semibold text-text-strong">This disease record is unavailable right now.</p>
        <p className="mt-2 text-sm text-text-muted">The backend API could not be reached. Please try again shortly.</p>
        <Link href="/diseases" className="mt-4 inline-block text-sm font-semibold text-brand-700 hover:underline dark:text-brand-400">
          Back to Disease Library
        </Link>
      </Container>
    );
  }

  return (
    <Container className="max-w-6xl py-12">
      <nav className="text-sm text-text-muted">
        <Link href="/" className="hover:text-brand-700 dark:hover:text-brand-400">
          Home
        </Link>{" "}
        &gt;{" "}
        <Link href="/diseases" className="hover:text-brand-700 dark:hover:text-brand-400">
          Diseases
        </Link>{" "}
        &gt; <span className="text-text-strong">{disease.name}</span>
      </nav>

      <Reveal className="mt-6 grid gap-10 lg:grid-cols-[1fr_1.3fr]">
        <div className="relative aspect-square overflow-hidden rounded-2xl border border-border-default bg-gradient-to-br from-brand-500/10 to-brand-600/15 shadow-sm shadow-black/5">
          <DiseaseImage id={disease.id} name={disease.name} plant={disease.plant} sizes="(min-width: 1024px) 40vw, 90vw" iconClassName="h-24 w-24" />
        </div>

        <div>
          <h1 className="text-3xl font-bold text-text-strong">{disease.name}</h1>
          {disease.description && <p className="mt-4 text-text-body">{disease.description}</p>}

          <div className="mt-6 flex flex-wrap gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Affected Plant</p>
              <p className="mt-1 font-semibold text-text-strong">{disease.plant}</p>
            </div>
            {disease.severity && (
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Severity</p>
                <p className="mt-1">
                  <Badge tone={severityTone(disease.severity)}>{disease.severity}</Badge>
                </p>
              </div>
            )}
          </div>
        </div>
      </Reveal>

      <div className="mt-10">
        <DiseaseInfoSections disease={disease} />
      </div>

      {(() => {
        const related = allDiseases
          .filter((d) => d.id !== disease.id && d.plant === disease.plant)
          .slice(0, 4);
        if (related.length === 0) return null;
        return (
          <Reveal className="mt-14">
            <h2 className="text-lg font-bold text-text-strong">Related {disease.plant} Diseases</h2>
            <div className="mt-5 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {related.map((d) => (
                <DiseaseCard key={d.id} disease={d} />
              ))}
            </div>
          </Reveal>
        );
      })()}

      <Reveal className="mt-14 flex flex-col items-center gap-4 rounded-2xl border border-brand-600/15 bg-gradient-to-br from-brand-500/10 to-brand-600/5 px-6 py-10 text-center">
        <LeafIcon className="h-8 w-8 text-brand-600 dark:text-brand-400" />
        <h2 className="text-xl font-bold text-text-strong">Think your plant might have {disease.name}?</h2>
        <p className="max-w-md text-sm text-text-body">
          Upload a photo of the affected leaf and get an instant AI diagnosis with a Grad-CAM
          explanation of what the model saw.
        </p>
        <LinkButton href="/diagnose" variant="primary" size="lg">
          Diagnose Your Plant
        </LinkButton>
      </Reveal>

      <ResponsibleUseDisclaimer className="mt-10" />
    </Container>
  );
}
