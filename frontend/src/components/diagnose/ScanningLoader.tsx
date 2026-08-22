export function ScanningLoader({ previewUrl }: { previewUrl: string }) {
  return (
    <div className="flex flex-col items-center gap-6 py-8">
      <div className="relative h-64 w-64 sm:h-80 sm:w-80">
        <div className="absolute -inset-3 animate-pulse-glow rounded-[2rem] bg-brand-500/20 blur-xl" aria-hidden="true" />
        <div className="relative h-full w-full overflow-hidden rounded-2xl border border-border-default shadow-lg shadow-black/10">
          {/* eslint-disable-next-line @next/next/no-img-element -- transient local object URL, not an optimizable asset */}
          <img src={previewUrl} alt="Uploaded leaf preview being analyzed" className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-brand-900/15" />
          <div className="animate-scan-sweep absolute inset-x-0 h-1/3 bg-gradient-to-b from-transparent via-brand-300/60 to-transparent" />
          <div className="absolute inset-3 rounded-xl border border-brand-300/40" />
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="relative flex h-3 w-3">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75" />
          <span className="relative inline-flex h-3 w-3 rounded-full bg-brand-600" />
        </span>
        <div className="text-left">
          <p className="font-semibold text-text-strong">AI Scanning&hellip;</p>
          <p className="text-sm text-text-muted">Analyzing leaf health</p>
        </div>
      </div>
    </div>
  );
}
