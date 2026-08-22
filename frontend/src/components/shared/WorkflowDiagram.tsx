import type { ReactNode } from "react";
import { Reveal } from "@/components/ui/Reveal";

export type WorkflowStep = {
  number: string;
  icon: ReactNode;
  title: string;
  desc: string;
};

export function WorkflowDiagram({
  steps,
  variant = "full",
}: {
  steps: WorkflowStep[];
  variant?: "compact" | "full";
}) {
  return (
    <div className="relative">
      {/* Connecting line: vertical rail on mobile, horizontal on md+, with a traveling pulse dot */}
      <div
        className="absolute left-8 top-8 bottom-8 w-0.5 bg-gradient-to-b from-brand-300/60 via-brand-400/40 to-brand-300/60 dark:from-brand-700/50 dark:via-brand-600/30 dark:to-brand-700/50 md:hidden"
        aria-hidden="true"
      >
        <span className="animate-travel-y absolute left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-brand-400 shadow-[0_0_8px_2px_rgba(74,222,128,0.55)]" />
      </div>
      <div
        className="absolute left-8 right-8 top-8 hidden h-0.5 bg-gradient-to-r from-brand-300/60 via-brand-400/40 to-brand-300/60 dark:from-brand-700/50 dark:via-brand-600/30 dark:to-brand-700/50 md:block"
        aria-hidden="true"
      >
        <span className="animate-travel-x absolute top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-brand-400 shadow-[0_0_8px_2px_rgba(74,222,128,0.55)]" />
      </div>
      <div
        className={`flex flex-col gap-10 md:grid md:gap-6 ${
          variant === "compact" ? "md:grid-cols-3" : "md:grid-cols-5"
        }`}
      >
        {steps.map((step, i) => (
          <Reveal
            key={step.number}
            delay={i * 80}
            className="group relative flex items-center gap-4 text-left md:flex-col md:items-center md:gap-3 md:text-center"
          >
            <div className="relative flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border border-border-default bg-surface-card text-brand-600 shadow-sm shadow-black/5 transition-all duration-300 group-hover:-translate-y-1 group-hover:border-brand-600/40 group-hover:shadow-lg group-hover:shadow-black/10 dark:text-brand-400">
              {step.icon}
              <span className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-brand-600 text-[10px] font-bold text-white">
                {step.number}
              </span>
            </div>
            <div>
              <p className="font-semibold text-text-strong">{step.title}</p>
              <p className="mt-1 max-w-[16rem] text-sm text-text-muted md:mt-0">{step.desc}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  );
}
