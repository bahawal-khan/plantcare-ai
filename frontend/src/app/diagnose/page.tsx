import type { Metadata } from "next";
import { DiagnoseFlow } from "@/components/diagnose/DiagnoseFlow";
import { Container } from "@/components/ui/Container";

export const metadata: Metadata = {
  title: "Diagnose Your Plant — PlantCare AI",
  description: "Upload a leaf image and get an instant AI-powered disease diagnosis with Grad-CAM explainability.",
};

export default function DiagnosePage() {
  return (
    <Container className="max-w-5xl py-12">
      <DiagnoseFlow />
    </Container>
  );
}
