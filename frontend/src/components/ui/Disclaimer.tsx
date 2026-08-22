export function ResponsibleUseDisclaimer({ className = "" }: { className?: string }) {
  return (
    <p
      className={`rounded-xl border border-brand-600/15 bg-brand-500/5 px-4 py-3 text-sm text-text-body ${className}`}
    >
      <strong className="font-semibold text-text-strong">Disclaimer:</strong> This is an AI-generated
      result and not a replacement for expert agronomic or plant-pathology diagnosis. Confidence
      scores reflect the model&apos;s certainty, not biological ground truth. The model was trained
      and evaluated on leaf photos captured under controlled, lab-like conditions, so accuracy on
      real-world field photos (cluttered backgrounds, variable lighting, multiple or overlapping
      leaves) may be lower than the reported evaluation metrics.
    </p>
  );
}

export function GradCamDisclaimer({ className = "" }: { className?: string }) {
  return (
    <p className={`text-xs text-text-muted ${className}`}>
      Grad-CAM highlights the image regions that most influenced this prediction. It is an
      interpretability aid, not proof of biological causation. The 3D view is only an interactive
      rendering of this same 2D heatmap &mdash; it is not a biological 3D scan or true 3D disease
      localization.
    </p>
  );
}
