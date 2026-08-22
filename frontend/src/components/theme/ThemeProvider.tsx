"use client";

import { createContext, useCallback, useContext, type ReactNode } from "react";

type Theme = "light" | "dark";

const STORAGE_KEY = "plantcare-theme";

const ThemeContext = createContext<{ toggleTheme: () => void } | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  // The inline `themeInitScript` (see below) already sets the `.dark` class
  // before hydration, so no React state/effect is needed to track the
  // current theme -- ThemeToggle renders both icons and lets CSS (the
  // `dark:` variant) decide which one is visible, avoiding a hydration
  // mismatch between server-rendered and client-detected theme.
  const toggleTheme = useCallback(() => {
    const root = document.documentElement;
    const next: Theme = root.classList.contains("dark") ? "light" : "dark";
    root.classList.toggle("dark", next === "dark");
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  return <ThemeContext.Provider value={{ toggleTheme }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}

/** Inline script source (no-FOUC): sets the `.dark` class before hydration. */
export const themeInitScript = `
(function () {
  try {
    var stored = window.localStorage.getItem("${STORAGE_KEY}");
    var theme = stored || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    if (theme === "dark") document.documentElement.classList.add("dark");
  } catch (e) {}
})();
`;
