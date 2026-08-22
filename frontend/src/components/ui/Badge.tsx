export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: "neutral" | "danger" | "success" | "warning";
  children: React.ReactNode;
}) {
  const toneClasses = {
    neutral: "bg-surface-muted text-text-body",
    danger: "bg-red-500/10 text-red-600 dark:text-red-400",
    success: "bg-brand-500/10 text-brand-700 dark:text-brand-400",
    warning: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
  }[tone];

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${toneClasses}`}>
      {children}
    </span>
  );
}
