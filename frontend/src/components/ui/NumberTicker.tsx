"use client";

import { useEffect, useState } from "react";
import { useInView } from "@/lib/use-in-view";

/**
 * Counts up from 0 to `value` once the tile scrolls into view. Initial
 * render is always "0" on server and client (same hydration-safe pattern as
 * Reveal/useInView) -- the count-up only starts client-side after mount, and
 * is skipped in favor of the final value under prefers-reduced-motion.
 */
export function NumberTicker({
  value,
  format = (n) => Math.round(n).toLocaleString(),
  duration = 1200,
  className = "",
}: {
  value: number;
  format?: (n: number) => string;
  duration?: number;
  className?: string;
}) {
  const { ref, inView } = useInView<HTMLSpanElement>();
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!inView) return;

    let frameId = 0;

    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      frameId = requestAnimationFrame(() => setDisplay(value));
      return () => cancelAnimationFrame(frameId);
    }

    const start = performance.now();

    function tick(now: number) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) frameId = requestAnimationFrame(tick);
    }

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [inView, value, duration]);

  return (
    <span ref={ref} className={className}>
      {format(display)}
    </span>
  );
}
