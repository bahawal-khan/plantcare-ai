"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Reports whether the ref'd element has scrolled into view (once, then stays
 * true). Initial state is always `false` on both server and client so the
 * first client render matches SSR output exactly -- browser-only capability
 * detection (IntersectionObserver support) and the observer subscription
 * itself only run inside the effect, i.e. after client mount.
 */
export function useInView<T extends HTMLElement>(options?: IntersectionObserverInit) {
  const ref = useRef<T | null>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || typeof IntersectionObserver === "undefined") {
      setInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px", ...options },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [options]);

  return { ref, inView };
}
