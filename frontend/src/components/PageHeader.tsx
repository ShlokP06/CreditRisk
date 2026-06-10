interface Props { title: string; subtitle?: string }

export function PageHeader({ title, subtitle }: Props) {
  return (
    <div className="sticky top-0 z-30 px-8 py-5" style={{ background: '#080B10', borderBottom: '1px solid #1D2433' }}>
      <h1 className="text-[16px] font-semibold text-ink" style={{ letterSpacing: '-0.01em' }}>{title}</h1>
      {subtitle && <p className="font-mono text-[12px] text-ink-3 mt-0.5">{subtitle}</p>}
    </div>
  );
}
