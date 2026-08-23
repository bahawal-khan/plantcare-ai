"use client";

import { useState } from "react";
import { SegmentedTabs } from "@/components/ui/SegmentedTabs";

type ViewMode = "original" | "heatmap" | "overlay";

export function GradCam2D({
  originalUrl,
  heatmapBase64,
  overlayBase64,
}: {
  originalUrl: string;
  heatmapBase64: string;
  overlayBase64: string;
}) {
  const heatmapUrl = `data:image/png;base64,${heatmapBase64}`;
  const overlayUrl = `data:image/png;base64,${overlayBase64}`;
  const [view, setView] = useState<ViewMode>("overlay");

  const images: Record<ViewMode, { src: string; alt: string; label: string }> = {
    original: { src: originalUrl, alt: "Original uploaded leaf", label: "Original Image" },
    heatmap: {
      src: heatmapUrl,
      alt: "Grad-CAM raw heatmap showing regions that influenced the prediction",
      label: "Grad-CAM Heatmap",
    },
    overlay: {
      src: overlayUrl,
      alt: "Grad-CAM heatmap overlay highlighting regions that influenced the prediction",
      label: "AI Attention Overlay",
    },
  };

  const active = images[view];

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
        <p className="min-w-0 flex-1 truncate text-sm font-semibold text-text-strong">{active.label}</p>
        <SegmentedTabs
          ariaLabel="Grad-CAM view"
          className="shrink-0"
          tabs={[
            { value: "original", label: "Original" },
            { value: "heatmap", label: "Heatmap" },
            { value: "overlay", label: "Overlay" },
          ]}
          value={view}
          onChange={(v) => setView(v as ViewMode)}
        />
      </div>

      <div className="mt-3 overflow-hidden rounded-2xl border border-border-default shadow-sm shadow-black/5">
        {/* eslint-disable-next-line @next/next/no-img-element -- local object URL / base64 data URI, not a static asset */}
        <img key={view} src={active.src} alt={active.alt} className="aspect-square w-full animate-fade-in object-cover" />
      </div>

      <div className="mt-3 grid grid-cols-3 gap-3">
        {(Object.keys(images) as ViewMode[]).map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setView(key)}
            aria-label={`Show ${images[key].label}`}
            aria-pressed={view === key}
            className={`overflow-hidden rounded-lg border transition-colors ${
              view === key ? "border-brand-600" : "border-border-default hover:border-brand-600/40"
            }`}
          >
            {/* eslint-disable-next-line @next/next/no-img-element -- local/base64 sources */}
            <img src={images[key].src} alt={images[key].alt} className="aspect-square w-full object-cover" />
          </button>
        ))}
      </div>
    </div>
  );
}
