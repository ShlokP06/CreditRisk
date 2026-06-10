'use client';
import { useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { ScoreForm } from '@/components/ScoreForm';
import { ScoreResult } from '@/components/ScoreResult';
import type { ScoreResult as TScoreResult } from '@/lib/types';

function EmptyState() {
  return (
    <div className="min-h-[440px] flex flex-col items-center justify-center gap-1 text-center">
      <p className="font-mono text-[11px] tracking-widest text-ink-3 uppercase">Awaiting transaction</p>
    </div>
  );
}

export default function ScorePage() {
  const [result,  setResult]  = useState<TScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  const handleSubmit = async (fn: () => Promise<TScoreResult>) => {
    setLoading(true); setError(null); setResult(null);
    try   { setResult(await fn()); }
    catch (e) { setError(e instanceof Error ? e.message : 'Request failed'); }
    finally   { setLoading(false); }
  };

  return (
    <>
      <PageHeader
        title="Score a Transaction"
        subtitle="Enter a card ID and amount. 17 fraud indicators are auto-enriched from the 590k-row IEEE-CIS database."
      />
      <div className="px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
          <div className="lg:col-span-2">
            <div className="bg-surface rounded-2xl p-6 shadow-card">
              <ScoreForm onSubmit={handleSubmit} loading={loading} />
            </div>

            {error && (
              <div
                className="mt-3 px-4 py-3 rounded-xl text-[13px] font-mono"
                style={{ color: '#FF4060', background: 'rgba(255,64,96,0.07)', border: '1px solid rgba(255,64,96,0.18)' }}
              >
                {error}
              </div>
            )}
          </div>

          <div className="lg:col-span-3">
            {result ? <ScoreResult result={result} /> : <EmptyState />}
          </div>
        </div>
      </div>
    </>
  );
}
