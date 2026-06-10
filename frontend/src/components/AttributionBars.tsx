import type { FeatureContributor } from '@/lib/types';

export function AttributionBars({ contributors }: { contributors: FeatureContributor[] }) {
  const max = Math.max(...contributors.map(c => Math.abs(c.attribution)), 0.001);
  return (
    <div className="space-y-3">
      {contributors.map((c, i) => {
        const pct = (Math.abs(c.attribution) / max) * 100;
        const pos = c.attribution > 0;
        const col = pos ? '#FF4060' : '#00D98B';
        return (
          <div key={i} className="flex items-center gap-3">
            <span className="font-mono text-[11px] text-ink-2 w-36 shrink-0 truncate">{c.feature}</span>
            <div className="flex-1 h-[5px] rounded-full bg-border overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{ width: `${pct}%`, background: col }}
              />
            </div>
            <span className="font-mono text-[11px] w-14 text-right shrink-0" style={{ color: col }}>
              {pos ? '+' : ''}{c.attribution.toFixed(3)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
