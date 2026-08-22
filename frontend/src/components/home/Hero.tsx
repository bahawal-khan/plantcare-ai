import Image from "next/image";
import { LinkButton, ScanRingCTA } from "@/components/ui/Button";
import { LeafIcon, ScanIcon, SparklesIcon } from "@/components/ui/icons";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 -z-20 bg-dot-grid" aria-hidden="true" />
      <div
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_50%_at_80%_10%,rgba(187,247,209,0.4),transparent),radial-gradient(50%_40%_at_10%_90%,rgba(220,252,232,0.5),transparent)] dark:bg-[radial-gradient(60%_50%_at_80%_10%,rgba(13,92,48,0.25),transparent),radial-gradient(50%_40%_at_10%_90%,rgba(10,61,33,0.25),transparent)]"
        aria-hidden="true"
      />

      <div className="mx-auto grid max-w-7xl gap-14 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:items-center lg:px-8 lg:py-24">
        <div className="animate-fade-up">
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-600/20 bg-brand-500/10 px-4 py-1.5 text-xs font-semibold text-brand-700 dark:text-brand-400">
            <SparklesIcon className="h-4 w-4" /> AI-Powered Plant Disease Detection
          </span>
          <h1 className="mt-6 text-4xl font-extrabold leading-[1.1] tracking-tight text-text-strong sm:text-5xl lg:text-[3.25rem]">
            Healthy Plants,
            <br />
            <span className="bg-gradient-to-r from-brand-600 to-brand-500 bg-clip-text text-transparent dark:from-brand-400 dark:to-brand-300">
              Better Future.
            </span>
          </h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-text-body sm:text-lg">
            Upload a leaf image and let our deep learning model detect diseases instantly, backed
            by a transparent Grad-CAM explanation of what the model actually saw.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <ScanRingCTA href="/diagnose">
              <LeafIcon className="h-4 w-4" /> Diagnose My Plant
            </ScanRingCTA>
            <LinkButton href="/diseases" variant="secondary" size="lg">
              Explore Diseases
            </LinkButton>
          </div>
        </div>

        <div className="relative mx-auto flex aspect-square w-full max-w-[20rem] items-center justify-center sm:max-w-[26rem]">
          {/* Layered glow */}
          <div className="absolute inset-0 rounded-[3rem] bg-gradient-to-br from-brand-200/70 to-brand-50/40 blur-2xl dark:from-brand-800/30 dark:to-brand-900/10" />
          <div
            className="absolute inset-6 rounded-[2.5rem] border border-dashed border-brand-400/40 [animation:spin_22s_linear_infinite] dark:border-brand-500/25"
            aria-hidden="true"
          />

          {/* Real leaf photo, framed as an AI scan target */}
          <div className="animate-float-slow relative h-56 w-56 overflow-hidden rounded-[2rem] border border-border-default shadow-xl shadow-black/15 sm:h-64 sm:w-64">
            <Image
              src="/diseases/tomato-early-blight.jpg"
              alt="Plant leaf being analyzed by PlantCare AI"
              fill
              sizes="(min-width: 1024px) 26rem, 80vw"
              className="object-cover"
              priority
            />

            {/* Grad-CAM style attention hotspot (illustrative, not a real inference result) */}
            <div
              className="pointer-events-none absolute inset-0 mix-blend-screen"
              style={{
                background:
                  "radial-gradient(circle at 60% 40%, rgba(255,110,30,0.55), rgba(255,210,40,0.3) 32%, transparent 62%)",
              }}
              aria-hidden="true"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink-900/45 via-transparent to-ink-900/10" />

            {/* Scanning sweep */}
            <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-[2rem]">
              <div className="animate-scan-sweep absolute inset-x-0 h-1/3 bg-gradient-to-b from-transparent via-white/30 to-transparent" />
            </div>

            {/* Viewfinder corner brackets */}
            <div className="pointer-events-none absolute left-3 top-3 h-5 w-5 border-l-2 border-t-2 border-white/70" aria-hidden="true" />
            <div className="pointer-events-none absolute right-3 top-3 h-5 w-5 border-r-2 border-t-2 border-white/70" aria-hidden="true" />
            <div className="pointer-events-none absolute bottom-3 left-3 h-5 w-5 border-b-2 border-l-2 border-white/70" aria-hidden="true" />
            <div className="pointer-events-none absolute bottom-3 right-3 h-5 w-5 border-b-2 border-r-2 border-white/70" aria-hidden="true" />
          </div>

          {/* Floating confidence / analysis chip */}
          <div className="absolute bottom-0 right-0 flex items-center gap-2.5 rounded-2xl border border-border-default bg-surface-card px-4 py-3 shadow-lg shadow-black/10 sm:bottom-4 sm:right-[-0.5rem]">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-600" />
            </span>
            <div className="text-xs">
              <p className="font-semibold text-text-strong">AI Scanning&hellip;</p>
              <p className="text-text-muted">Analyzing leaf health</p>
            </div>
          </div>

          {/* Floating explainability chip */}
          <div className="absolute left-[-0.5rem] top-2 hidden items-center gap-2 rounded-xl border border-border-default bg-surface-card px-3 py-2 shadow-lg shadow-black/10 sm:flex">
            <ScanIcon className="h-4 w-4 text-brand-600 dark:text-brand-400" />
            <p className="text-xs font-semibold text-text-strong">Grad-CAM Explainable</p>
          </div>
        </div>
      </div>
    </section>
  );
}
