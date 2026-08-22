"use client";

import { useTheme } from "@/components/theme/ThemeProvider";
import { MoonIcon, SunIcon } from "@/components/ui/icons";

export function ThemeToggle({ className = "" }: { className?: string }) {
  const { toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label="Toggle light/dark theme"
      className={`relative inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border-default text-text-body transition-colors hover:border-brand-600/40 hover:text-brand-600 ${className}`}
    >
      <SunIcon className="h-[18px] w-[18px] dark:hidden" />
      <MoonIcon className="hidden h-[18px] w-[18px] dark:block" />
    </button>
  );
}
