"use client";

import type { ReactNode } from "react";
import { StatTile } from "./StatTile";
import { NumberTicker } from "./NumberTicker";

/**
 * StatTile with a count-up value. Kept as a separate client component
 * (rather than passing a format function as a prop into a client component
 * from a server page) because inline functions can't cross the
 * server-to-client boundary in RSC -- `kind` is a plain, serializable string
 * instead.
 */
export function AnimatedStatTile({
  icon,
  value,
  kind,
  label,
}: {
  icon: ReactNode;
  value: number;
  kind: "plus" | "percent";
  label: string;
}) {
  const format = kind === "percent" ? (n: number) => `${n.toFixed(1)}%` : (n: number) => `${Math.round(n)}+`;
  return <StatTile icon={icon} value={<NumberTicker value={value} format={format} />} label={label} />;
}
