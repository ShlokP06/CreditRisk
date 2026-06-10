type Band = 'low' | 'medium' | 'high';

const CFG: Record<Band, { fg: string; bg: string; label: string }> = {
  low:    { fg: '#00D98B', bg: 'rgba(0,217,139,0.1)',   label: 'Low Risk'    },
  medium: { fg: '#F0A428', bg: 'rgba(240,164,40,0.1)',   label: 'Medium Risk' },
  high:   { fg: '#FF4060', bg: 'rgba(255,64,96,0.1)',    label: 'High Risk'   },
};

export function RiskBadge({ band }: { band: string }) {
  const c = CFG[band as Band] ?? CFG.medium;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold"
      style={{ color: c.fg, background: c.bg }}
    >
      <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: c.fg }} />
      {c.label}
    </span>
  );
}
