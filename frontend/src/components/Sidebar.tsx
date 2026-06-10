'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import clsx from 'clsx';
import { Zap, Code2, Bell } from 'lucide-react';
import { getHealth } from '@/lib/api';
import type { HealthStatus } from '@/lib/types';

const NAV = [
  { href: '/score',  label: 'Score',        Icon: Zap   },
  { href: '/api',    label: 'API Explorer',  Icon: Code2 },
  { href: '/alerts', label: 'Alerts',        Icon: Bell  },
];

const SERVICES = ['gateway', 'feature', 'scoring', 'alert', 'ingestion'];

export function Sidebar() {
  const path = usePathname();
  const [health, setHealth] = useState<HealthStatus>({});
  const loaded = Object.keys(health).length > 0;

  useEffect(() => {
    const load = () => getHealth().then(setHealth).catch(() => {});
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, []);

  return (
    <aside
      className="fixed left-0 top-0 bottom-0 w-[220px] flex flex-col z-40"
      style={{ background: '#080B10', borderRight: '1px solid #1D2433' }}
    >
      <div className="h-14 px-5 flex items-center gap-3 shrink-0" style={{ borderBottom: '1px solid #1D2433' }}>
        <div className="min-w-0">
          <p className="font-mono text-[13px] font-semibold tracking-[0.12em] text-ink leading-tight">CR</p>
          <p className="font-mono text-[9px] tracking-[0.22em] text-ink-3 leading-tight uppercase">Intelligence</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
        {NAV.map(({ href, label, Icon }) => {
          const active = path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] transition-colors',
                active
                  ? 'text-ink'
                  : 'text-ink-3 hover:text-ink-2 hover:bg-surface-2'
              )}
              style={active ? { background: 'rgba(237,240,247,0.05)' } : undefined}
            >
              <Icon className="w-4 h-4 shrink-0" strokeWidth={active ? 2 : 1.5} />
              <span className={active ? 'font-medium' : ''}>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 shrink-0" style={{ borderTop: '1px solid #1D2433' }}>
        <p className="font-mono text-[9px] tracking-[0.2em] text-ink-3 uppercase mb-3">Services</p>
        <div className="space-y-2">
          {SERVICES.map(svc => {
            const st = health[svc];
            const dotColor = !loaded
              ? '#263044'
              : st === 'ok'   ? '#00D98B'
              : st === 'down' ? '#FF4060'
              : '#F0A428';
            return (
              <div key={svc} className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: dotColor }} />
                <span className="text-[12px] text-ink-3 flex-1 capitalize">{svc}</span>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
