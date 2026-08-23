import type { HTMLAttributes, ReactNode } from "react";

type Variant = "surface" | "elevated" | "inset" | "glass";

const variantClasses: Record<Variant, string> = {
  surface: "border border-border-default bg-surface-card",
  elevated: "border border-border-default bg-surface-card shadow-sm shadow-black/5",
  inset: "border border-border-default bg-surface-inset",
  glass: "border border-white/15 bg-surface-card/70 backdrop-blur-md shadow-lg shadow-black/10",
};

export function Card({
  children,
  variant = "surface",
  className = "",
  ...props
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode; variant?: Variant }) {
  return (
    <div
      className={`rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/10 ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
