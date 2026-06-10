import type { ScoreResult } from '@/lib/types';
import { ScoreGauge } from './ScoreGauge';
import { AttributionBars } from './AttributionBars';

const RISK_CFG: Record<string, { label: string; color: string; rgb: string }> = {
  low:    { label: 'LOW RISK',    color: '#00D98B', rgb: '0,217,139'   },
  medium: { label: 'MEDIUM RISK', color: '#F0A428', rgb: '240,164,40'  },
  high:   { label: 'HIGH RISK',   color: '#FF4060', rgb: '255,64,96'   },
};

export function ScoreResult({ result }: { result: ScoreResult }) {
  const score = Math.round(result.risk_score * 100);
  const cfg   = RISK_CFG[result.risk_band] ?? RISK_CFG.medium;

  return (
    <div className="bg-surface rounded-2xl shadow-card overflow-hidden">
      <div
        className="px-6 py-3 flex items-center justify-between"
        style={{ background: `rgba(${cfg.rgb}, 0.06)` }}
      >
        <span className="font-mono text-[11px] text-ink-3">{result.transaction_id}</span>
        <span
          className="font-mono text-[11px] font-semibold tracking-widest uppercase"
          style={{ color: cfg.color }}
        >
          {cfg.label}
        </span>
      </div>

      <div className="px-6 pt-8 pb-6 flex flex-col items-center gap-4">
        <ScoreGauge score={score} size={200} />

        <div className="flex items-center gap-3 font-mono text-[11px] text-ink-3">
          <span>{result.model_version}</span>
          <span className="text-border-strong">·</span>
          <span>{result.risk_score.toFixed(4)}</span>
          {result.enriched && (
            <>
              <span className="text-border-strong">·</span>
              <span style={{ color: '#48566A' }}>db-enriched</span>
            </>
          )}
        </div>

        {result.alerted && (
          <div
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg font-mono text-[12px]"
            style={{ background: 'rgba(255,64,96,0.06)', color: '#FF4060' }}
          >
            <span>⚡</span>
            <span>Alert triggered — see Alerts feed</span>
          </div>
        )}
      </div>

      {result.top_contributors.length > 0 && (
        <div className="px-6 py-5 border-t border-border">
          <p className="font-mono text-[10px] tracking-widest text-ink-3 uppercase mb-4">Risk Factors</p>
          <AttributionBars contributors={result.top_contributors} />
        </div>
      )}
    </div>
  );
}
