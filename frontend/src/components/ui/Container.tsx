import type { ElementType, ReactNode } from "react";

export function Container({
  children,
  as: Tag = "div",
  className = "",
}: {
  children: ReactNode;
  as?: ElementType;
  className?: string;
}) {
  return <Tag className={`mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 ${className}`}>{children}</Tag>;
}
