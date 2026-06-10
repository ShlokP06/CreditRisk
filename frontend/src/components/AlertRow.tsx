'use client';
import { useState } from 'react';
import type { Alert } from '@/lib/types';
import { RiskBadge } from './RiskBadge';
import { ChevronDown, ChevronUp } from 'lucide-react';

function timeAgo(dt: string) {
  const s = (Date.now() - new Date(dt).getTime()) / 1000;
  if (s < 60)   return `${Math.round(s)}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  return `${Math.round(s / 3600)}h ago`;
}

export function AlertRow({ alert }: { alert: Alert }) {
  const [open, setOpen] = useState(false);
  const score = Math.round(alert.risk_score * 100);
  const col   = score < 33 ? '#00D98B' : score < 67 ? '#F0A428' : '#FF4060';

  return (
    <div
      className="px-5 py-3.5 cursor-pointer transition-colors"
      style={open ? { background: '#171C2A' } : undefined}
      onMouseEnter={e => { if (!open) (e.currentTarget as HTMLDivElement).style.background = '#171C2A'; }}
      onMouseLeave={e => { if (!open) (e.currentTarget as HTMLDivElement).style.background = ''; }}
      onClick={() => setOpen(o => !o)}
    >
      <div className="flex items-center gap-4">
        <span
          className="font-mono font-bold text-lg w-9 text-right shrink-0 tabular-nums"
          style={{ color: col }}
        >
          {score}
        </span>
        <div className="flex-1 min-w-0 flex items-center gap-2">
          <span className="font-mono text-[12px] text-ink truncate">{alert.transaction_id}</span>
          <RiskBadge band={alert.risk_band} />
        </div>
        <span className="font-mono text-[11px] text-ink-3 shrink-0">{timeAgo(alert.created_at)}</span>
        <span className="text-ink-3 w-4 flex items-center justify-center shrink-0">
          {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </span>
      </div>
      {open && (
        <div className="mt-2.5 ml-[52px]">
          {alert.narration
            ? (
              <p
                className="text-[12px] text-ink-2 leading-relaxed"
                style={{ background: 'rgba(237,240,247,0.03)', borderRadius: 4, padding: '8px 12px' }}
              >
                {alert.narration}
              </p>
            )
            : <p className="font-mono text-[11px] text-ink-3 italic">Generating narration...</p>}
        </div>
      )}
    </div>
  );
}
