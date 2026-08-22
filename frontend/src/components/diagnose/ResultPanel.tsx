"use client";

import { useState } from "react";
import Link from "next/link";
import type { DiseaseRecord, PredictionResponse } from "@/lib/types";
import { formatPercent, titleCase } from "@/lib/format";
import { findMatchingDisease } from "@/lib/disease-match";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { SegmentedTabs } from "@/components/ui/SegmentedTabs";
import { ResponsibleUseDisclaimer, GradCamDisclaimer } from "@/components/ui/Disclaimer";
import { ScanIcon } from "@/components/ui/icons";
import { DiseaseInfoSections } from "@/components/diseases/DiseaseInfoSections";
import { GradCam2D } from "./GradCam2D";
import { GradCam3D } from "./GradCam3D";

type ResultTab = "diagnosis" | "visual" | "details";

export function ResultPanel({
  result,
  previewUrl,
  diseases,
}: {
  result: PredictionResponse;
  previewUrl: string;
  diseases: DiseaseRecord[];
}) {
  const [tab, setTab] = useState<ResultTab>("diagnosis");
  const isHealthy = result.disease.toLowerCase() === "healthy";
  const matchedDisease = findMatchingDisease(diseases, result.plant, result.disease);

  return (
    <div className="animate-fade-up">
      <nav className="mb-4 text-sm text-text-muted">
        <Link href="/" className="hover:text-brand-700 dark:hover:text-brand-400">
          Home
        </Link>{" "}
        &gt;{" "}
        <Link href="/diagnose" className="hover:text-brand-700 dark:hover:text-brand-400">
          Diagnose
        </Link>{" "}
        &gt; <span className="text-text-strong">Result</span>
      </nav>

      <div className="flex flex-wrap items-center gap-3">
        <Badge tone="success">Diagnostic Result</Badge>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold text-text-strong sm:text-3xl">
          {titleCase(result.plant)} &mdash; {titleCase(result.disease)}
        </h1>
        <Badge tone={isHealthy ? "success" : "danger"}>{isHealthy ? "Healthy" : "Diseased"}</Badge>
      </div>

      <SegmentedTabs
        className="mt-6"
        ariaLabel="Diagnostic result sections"
        value={tab}
        onChange={(v) => setTab(v as ResultTab)}
        tabs={[
          { value: "diagnosis", label: "Diagnosis" },
          { value: "visual", label: "Visual Explanation" },
          { value: "details", label: "Details" },
        ]}
      />

      {tab === "diagnosis" && (
        <div className="mt-6 grid gap-8 lg:grid-cols-[1.1fr_1fr]">
          <Card variant="elevated" className="p-6">
            <p className="text-sm font-medium text-text-muted">AI Confidence Score</p>
            <p className="mt-1 text-4xl font-bold text-brand-600 dark:text-brand-400">
              {formatPercent(result.confidence)}
            </p>
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-surface-muted">
              <div
                className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-600 transition-[width] duration-700"
                style={{ width: `${Math.min(result.confidence * 100, 100)}%` }}
              />
            </div>
            <p className="mt-3 text-sm text-text-body">
              Our AI model is {formatPercent(result.confidence)} confident that this plant is
              affected by {titleCase(result.disease)}.
            </p>

            {result.top_k.length > 1 && (
              <div className="mt-6 border-t border-border-default pt-5">
                <p className="text-sm font-semibold text-text-strong">Top Predictions</p>
                <ul className="mt-3 space-y-3">
                  {result.top_k.map((entry) => (
                    <li key={entry.rank}>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-text-body">
                          {titleCase(entry.plant)} &mdash; {titleCase(entry.disease)}
                        </span>
                        <span className="font-semibold text-text-strong">{formatPercent(entry.confidence)}</span>
                      </div>
                      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-surface-muted">
                        <div
                          className="h-full rounded-full bg-brand-400/70"
                          style={{ width: `${Math.min(entry.confidence * 100, 100)}%` }}
                        />
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>

          {/* eslint-disable-next-line @next/next/no-img-element -- transient local object URL */}
          <img
            src={previewUrl}
            alt="Uploaded leaf"
            className="aspect-square w-full rounded-2xl border border-border-default object-cover"
          />
        </div>
      )}

      {tab === "visual" && (
        <div className="mt-6">
          {result.gradcam ? (
            <>
              <Card variant="elevated" className="mx-auto max-w-sm p-4 sm:max-w-md">
                <GradCam2D
                  originalUrl={previewUrl}
                  heatmapBase64={result.gradcam.heatmap_png_base64}
                  overlayBase64={result.gradcam.overlay_png_base64}
                />
              </Card>

              <section className="mt-10">
                <div className="flex items-center justify-between">
                  <h2 className="flex items-center gap-2 text-lg font-bold text-text-strong">
                    <ScanIcon className="h-5 w-5 text-brand-600 dark:text-brand-400" />
                    Interactive 3D Grad-CAM Visualization
                  </h2>
                  <Badge tone="neutral">AI Interpretability</Badge>
                </div>
                <div className="mx-auto mt-4 max-w-xl">
                  <GradCam3D visualization={result.gradcam.visualization_3d} />
                </div>
                <GradCamDisclaimer className="mx-auto mt-3 max-w-xl" />
              </section>
            </>
          ) : (
            <div className="rounded-2xl border border-border-default bg-surface-inset p-8 text-center text-sm text-text-muted">
              Grad-CAM explainability data isn&apos;t available for this prediction.
            </div>
          )}
        </div>
      )}

      {tab === "details" && (
        <section className="mt-6">
          <h2 className="text-lg font-bold text-text-strong">
            About {titleCase(result.plant)} {titleCase(result.disease)}
          </h2>
          {matchedDisease?.description && <p className="mt-2 text-sm text-text-body">{matchedDisease.description}</p>}
          <div className="mt-4">
            {matchedDisease ? (
              <DiseaseInfoSections disease={matchedDisease} />
            ) : (
              <p className="rounded-xl border border-border-default bg-surface-inset p-4 text-sm text-text-muted">
                Detailed disease information for this class isn&apos;t in the disease library yet.
                {matchedDisease === null && !isHealthy && " Check back soon, or browse the "}
                {!isHealthy && (
                  <Link href="/diseases" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
                    Disease Library
                  </Link>
                )}
                {!isHealthy && "."}
              </p>
            )}
          </div>
        </section>
      )}

      <ResponsibleUseDisclaimer className="mt-10" />
    </div>
  );
}
