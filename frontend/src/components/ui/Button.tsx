import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-brand-600 text-white hover:bg-brand-700 shadow-sm shadow-brand-900/20",
  secondary:
    "bg-surface-card text-text-strong border border-border-default hover:border-brand-600/40 hover:text-brand-700",
  ghost: "text-text-strong hover:bg-surface-muted",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-4 py-2 text-xs",
  md: "px-6 py-3 text-sm",
  lg: "px-7 py-3.5 text-base",
};

const baseClasses =
  "inline-flex items-center justify-center gap-2 rounded-full font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50";

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size; children: ReactNode }) {
  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

/**
 * Primary CTA wrapper that reveals a slow rotating conic-gradient ring around
 * the button on hover -- a restrained nod to the "AI scanning" visual motif,
 * inspired by Aceternity's Moving Border / Hover Border Gradient pattern.
 * Invisible until hover so it never reads as decoration-for-its-own-sake.
 */
export function ScanRingCTA({
  href,
  size = "lg",
  className = "",
  children,
}: {
  href: string;
  size?: Size;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span className="group/cta relative inline-flex overflow-hidden rounded-full">
      <span
        aria-hidden="true"
        className="absolute inset-[-150%] opacity-0 [animation:spin_3s_linear_infinite] group-hover/cta:opacity-100"
        style={{
          background: "conic-gradient(from 0deg, transparent 0%, #4ade80 12%, transparent 30%)",
        }}
      />
      <LinkButton href={href} variant="primary" size={size} className={`relative m-[2px] ${className}`}>
        {children}
      </LinkButton>
    </span>
  );
}

export function LinkButton({
  href,
  variant = "primary",
  size = "md",
  className = "",
  children,
  onClick,
}: {
  href: string;
  variant?: Variant;
  size?: Size;
  className?: string;
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
    >
      {children}
    </Link>
  );
}
