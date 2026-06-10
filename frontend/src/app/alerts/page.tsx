'use client';
import { useEffect, useState } from 'react';
import { getAlerts } from '@/lib/api';
import type { Alert } from '@/lib/types';
import { AlertRow } from '@/components/AlertRow';
import { PageHeader } from '@/components/PageHeader';

export default function AlertsPage() {
  const [alerts, setAlerts]   = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = () =>
      getAlerts(50)
        .then(d => { setAlerts(d.alerts ?? []); setLoading(false); })
        .catch(() => setLoading(false));
    load();
    const id = setInterval(load, 10_000);
    return () => clearInterval(id);
  }, []);

  return (
    <>
      <PageHeader
        title="Alerts Feed"
        subtitle="High-risk transactions with LLM narrations. Auto-refreshes every 10s."
      />
      <div className="px-8 py-8 max-w-3xl">
        {loading ? (
          <div className="py-16 text-center font-mono text-[13px] text-ink-3">Loading...</div>
        ) : alerts.length === 0 ? (
          <div className="bg-surface rounded-2xl shadow-card px-6 py-16 text-center">
            <p className="text-[15px] font-semibold text-ink mb-1">No alerts yet</p>
            <p className="font-mono text-[12px] text-ink-3">Score a high-risk transaction to generate one.</p>
          </div>
        ) : (
          <div className="flex items-center justify-between mb-4">
            <span className="font-mono text-[12px] text-ink-3">{alerts.length} alerts</span>
          </div>
        )}

        {!loading && alerts.length > 0 && (
          <div className="bg-surface rounded-2xl shadow-card divide-y divide-border">
            {alerts.map(a => <AlertRow key={a.transaction_id} alert={a} />)}
          </div>
        )}
      </div>
    </>
  );
}
