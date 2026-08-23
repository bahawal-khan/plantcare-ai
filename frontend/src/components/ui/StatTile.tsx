export function StatTile({
  icon,
  value,
  label,
}: {
  icon: React.ReactNode;
  value: React.ReactNode;
  label: string;
}) {
  return (
    <div className="group relative flex min-w-0 flex-col items-center gap-1 overflow-hidden rounded-2xl border border-border-default bg-surface-card px-4 py-6 text-center shadow-sm shadow-black/5 transition-all duration-300 hover:-translate-y-1 hover:border-brand-600/30 hover:shadow-lg hover:shadow-black/10 sm:items-start sm:text-left">
      <div
        className="pointer-events-none absolute -left-8 -top-8 h-24 w-24 rounded-full bg-brand-500/0 blur-2xl transition-colors duration-500 group-hover:bg-brand-500/20"
        aria-hidden="true"
      />
      <div className="relative text-brand-600 dark:text-brand-400">{icon}</div>
      <p className="relative w-full break-words text-xl font-bold text-text-strong sm:text-2xl">{value}</p>
      <p className="relative text-sm text-text-muted">{label}</p>
    </div>
  );
}
