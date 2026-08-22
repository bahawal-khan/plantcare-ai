"use client";

import { useId, useRef } from "react";

export type SegmentedTab = { value: string; label: string };

export function SegmentedTabs({
  tabs,
  value,
  onChange,
  className = "",
  ariaLabel = "Tabs",
}: {
  tabs: SegmentedTab[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
  ariaLabel?: string;
}) {
  const groupId = useId();
  const buttonRefs = useRef<Record<string, HTMLButtonElement | null>>({});

  function focusAndSelect(nextIndex: number) {
    const next = tabs[(nextIndex + tabs.length) % tabs.length];
    onChange(next.value);
    buttonRefs.current[next.value]?.focus();
  }

  return (
    <div
      role="tablist"
      aria-label={ariaLabel}
      className={`inline-flex items-center gap-1 rounded-full border border-border-default bg-surface-inset p-1 ${className}`}
    >
      {tabs.map((tab, i) => {
        const selected = tab.value === value;
        return (
          <button
            key={tab.value}
            ref={(el) => {
              buttonRefs.current[tab.value] = el;
            }}
            id={`${groupId}-${tab.value}`}
            role="tab"
            type="button"
            aria-selected={selected}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(tab.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight") {
                e.preventDefault();
                focusAndSelect(i + 1);
              } else if (e.key === "ArrowLeft") {
                e.preventDefault();
                focusAndSelect(i - 1);
              }
            }}
            className={`rounded-full px-4 py-1.5 text-sm font-semibold transition-colors ${
              selected ? "bg-brand-600 text-white shadow-sm" : "text-text-body hover:text-text-strong"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
