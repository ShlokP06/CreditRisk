interface Props { name: string; status?: string }
export function HealthDot({ name, status }: Props) {
  const bg = status === 'ok' ? '#22C55E' : status === 'down' ? '#EF4444' : '#52525B';
  return (
    <div className="flex items-center gap-2">
      <span className="rounded-full shrink-0" style={{ width: 6, height: 6, background: bg }} />
      <span className="font-mono text-[11px] text-ink-3">{name}</span>
    </div>
  );
}
