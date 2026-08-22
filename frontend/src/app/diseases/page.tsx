import type { Metadata } from "next";
import { getDiseasesSafe } from "@/lib/api";
import { DiseaseGrid } from "@/components/diseases/DiseaseGrid";
import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/ui/Reveal";

export const metadata: Metadata = {
  title: "Disease Library — PlantCare AI",
  description: "Explore information about the plant diseases PlantCare AI can detect.",
};

export const dynamic = "force-dynamic";

export default async function DiseaseLibraryPage() {
  const diseases = await getDiseasesSafe();

  return (
    <Container className="py-12">
      <Reveal className="text-center">
        <h1 className="text-3xl font-bold text-text-strong sm:text-4xl">Disease Library</h1>
        <p className="mt-2 text-text-body">Explore information about various plant diseases</p>
      </Reveal>
      <div className="mt-10">
        <DiseaseGrid diseases={diseases} />
      </div>
    </Container>
  );
}
