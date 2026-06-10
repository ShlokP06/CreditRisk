'use client';
import { useState } from 'react';
import { PageHeader } from '@/components/PageHeader';

const BASE = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8000';

interface Field {
  name: string; type: 'text' | 'number' | 'select' | 'textarea';
  placeholder?: string; options?: string[]; default?: string;
  required?: boolean; pathParam?: boolean; hint?: string;
}
interface Endpoint {
  method: 'GET' | 'POST'; path: string; title: string; desc: string;
  fields?: Field[]; tag: string;
}

const ENDPOINTS: Endpoint[] = [
  {
    method: 'POST', path: '/score-enriched', title: 'Score (Enriched)',
    tag: 'scoring',
    desc: 'Score a transaction with just a card ID and amount. Historical fraud indicators (c1–c14, match flags, email domain) are auto-fetched from the 590k-row PostgreSQL database.',
    fields: [
      { name: 'user_id',     type: 'text',   placeholder: '13926',  required: true,  hint: 'Card identifier (card1 in IEEE-CIS)' },
      { name: 'amount',      type: 'number', placeholder: '5000',   required: true,  hint: 'Transaction amount in USD' },
      { name: 'card_brand',  type: 'select', options: ['visa','mastercard','american express','discover'], default: 'visa' },
      { name: 'card_type',   type: 'select', options: ['credit','debit'], default: 'credit' },
      { name: 'product_cd',  type: 'select', options: ['W','H','C','S','R'], default: 'W' },
      { name: 'device_type', type: 'select', options: ['unknown','desktop','mobile'], default: 'unknown' },
    ],
  },
  {
    method: 'POST', path: '/score', title: 'Score (Full)',
    tag: 'scoring',
    desc: 'Score with all 25 fields manually specified. Useful for testing specific risk scenarios without database enrichment.',
    fields: [
      { name: 'transaction_id', type: 'text',   placeholder: 'txn_001',              required: true  },
      { name: 'user_id',        type: 'text',   placeholder: '13926',                required: true  },
      { name: 'merchant_id',    type: 'text',   placeholder: 'merch_x',              required: true  },
      { name: 'amount',         type: 'number', placeholder: '5000',                 required: true  },
      { name: 'timestamp',      type: 'text',   placeholder: '2024-01-15T02:30:00Z', required: true  },
      { name: 'product_cd',     type: 'select', options: ['W','H','C','S','R'],       default: 'C'    },
      { name: 'card_brand',     type: 'select', options: ['visa','mastercard','american express','discover'], default: 'discover' },
      { name: 'card_type',      type: 'select', options: ['credit','debit'],          default: 'debit' },
      { name: 'p_emaildomain',  type: 'text',   placeholder: 'anonymous.com'         },
      { name: 'device_type',    type: 'select', options: ['unknown','desktop','mobile'], default: 'unknown' },
      { name: 'c1',   type: 'number', placeholder: '25', hint: 'Billing addresses linked to card' },
      { name: 'c2',   type: 'number', placeholder: '5',  hint: 'Phone numbers linked to card'     },
      { name: 'c6',   type: 'number', placeholder: '3',  hint: 'Phones on billing address'        },
      { name: 'c13',  type: 'number', placeholder: '0'   },
      { name: 'c14',  type: 'number', placeholder: '0'   },
      { name: 'm1',   type: 'select', options: ['-1','0','1'], default: '0', hint: 'Name match flag' },
      { name: 'm2',   type: 'select', options: ['-1','0','1'], default: '0' },
      { name: 'm3',   type: 'select', options: ['-1','0','1'], default: '0' },
      { name: 'd1',   type: 'number', placeholder: '0',  hint: 'Days since last transaction' },
      { name: 'd4',   type: 'number', placeholder: '0'   },
      { name: 'addr1', type: 'number', placeholder: '-1', hint: 'Billing zip (-1 = unknown)' },
      { name: 'dist1', type: 'number', placeholder: '0',  hint: 'Billing–shipping distance (mi)' },
    ],
  },
  {
    method: 'GET', path: '/health', title: 'System Health',
    tag: 'system',
    desc: 'Returns the operational status of all 5 downstream microservices (feature, scoring, alert, ingestion) and the gateway itself.',
    fields: [],
  },
  {
    method: 'GET', path: '/alerts', title: 'Alert Feed',
    tag: 'alerts',
    desc: 'Retrieve the most recent high-risk transaction alerts, each with LLM-generated narration from the Groq llama-3.1-8b model.',
    fields: [
      { name: 'limit', type: 'number', placeholder: '50', hint: 'Max alerts to return (default 50, max 500)' },
    ],
  },
];

const TAG_STYLE: Record<string, { color: string; bg: string }> = {
  scoring: { color: '#7A8BA0', bg: 'rgba(122,139,160,0.1)' },
  system:  { color: '#00D98B', bg: 'rgba(0,217,139,0.08)'  },
  alerts:  { color: '#FF4060', bg: 'rgba(255,64,96,0.08)'  },
};

function highlightJson(json: string): string {
  return json
    .replace(/("(?:\\.|[^"\\])*")(\s*:)/g, '<span style="color:#7A8BA0">$1</span>$2')
    .replace(/:\s*("(?:\\.|[^"\\])*")/g, ': <span style="color:#00D98B">$1</span>')
    .replace(/:\s*(true|false)/g, ': <span style="color:#F0A428">$1</span>')
    .replace(/:\s*(null)/g, ': <span style="color:#48566A">$1</span>')
    .replace(/:\s*(-?\d+\.?\d*)/g, ': <span style="color:#EDF0F7">$1</span>');
}

function MethodBadge({ method }: { method: 'GET' | 'POST' }) {
  return (
    <span
      className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wide"
      style={
        method === 'POST'
          ? { color: '#7A8BA0', background: 'rgba(122,139,160,0.12)' }
          : { color: '#00D98B', background: 'rgba(0,217,139,0.1)'    }
      }
    >
      {method}
    </span>
  );
}

function EndpointCard({ ep }: { ep: Endpoint }) {
  const [open,     setOpen]     = useState(false);
  const [values,   setValues]   = useState<Record<string, string>>({});
  const [response, setResponse] = useState<unknown | null>(null);
  const [status,   setStatus]   = useState<number | null>(null);
  const [elapsed,  setElapsed]  = useState<number | null>(null);
  const [loading,  setLoading]  = useState(false);

  const set = (k: string, v: string) => setValues(prev => ({ ...prev, [k]: v }));

  const send = async () => {
    setLoading(true); setResponse(null);
    const t0 = performance.now();
    try {
      let url = `${BASE}${ep.path}`;
      const init: RequestInit = { method: ep.method };
      if (ep.method === 'POST') {
        const body: Record<string, unknown> = {};
        for (const f of ep.fields ?? []) {
          const v = values[f.name] ?? f.default ?? '';
          if (v !== '') body[f.name] = f.type === 'number' ? parseFloat(v) || 0 : v;
        }
        init.body = JSON.stringify(body);
        init.headers = { 'Content-Type': 'application/json' };
      } else {
        const params = new URLSearchParams();
        for (const f of ep.fields ?? []) {
          const v = values[f.name] ?? f.default ?? '';
          if (f.pathParam) url = url.replace(`{${f.name}}`, v);
          else if (v) params.set(f.name, v);
        }
        if (params.toString()) url += `?${params}`;
      }
      const res = await fetch(url, init);
      setStatus(res.status);
      setResponse(await res.json());
    } catch (e) {
      setStatus(0);
      setResponse({ error: e instanceof Error ? e.message : 'Network error' });
    } finally {
      setElapsed(Math.round(performance.now() - t0));
      setLoading(false);
    }
  };

  const inputCls = 'w-full h-8 px-2.5 rounded-md bg-bg border border-border-strong text-ink text-[12px] font-mono outline-none placeholder:text-ink-3';
  const labelCls = 'block font-mono text-[10px] uppercase tracking-widest text-ink-3 mb-1';
  const tag = TAG_STYLE[ep.tag] ?? TAG_STYLE.scoring;

  return (
    <div className="bg-surface rounded-xl shadow-card overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-5 py-4 text-left transition-colors hover:bg-surface-2"
        onClick={() => setOpen(o => !o)}
      >
        <MethodBadge method={ep.method} />
        <span className="font-mono text-[13px] text-ink-3">{ep.path}</span>
        <span className="font-semibold text-[13px] text-ink ml-1">{ep.title}</span>
        <span
          className="ml-auto font-mono text-[10px] px-2 py-0.5 rounded-full"
          style={{ color: tag.color, background: tag.bg }}
        >
          {ep.tag}
        </span>
        <span className="font-mono text-[11px] text-ink-3 ml-1">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-5 py-4 space-y-4 border-t border-border">
          <p className="text-[13px] text-ink-2 leading-relaxed">{ep.desc}</p>

          {(ep.fields ?? []).length > 0 && (
            <div className="grid grid-cols-2 gap-3">
              {ep.fields!.map(f => (
                <div key={f.name}>
                  <label className={labelCls}>
                    {f.name}
                    {f.required && <span className="text-ink-2 ml-1">*</span>}
                    {f.hint && <span className="text-ink-3 font-sans normal-case font-normal ml-1">— {f.hint}</span>}
                  </label>
                  {f.type === 'select' ? (
                    <select
                      className={inputCls}
                      value={values[f.name] ?? f.default ?? ''}
                      onChange={e => set(f.name, e.target.value)}
                    >
                      {f.options!.map(o => <option key={o} value={o}>{o}</option>)}
                    </select>
                  ) : (
                    <input
                      className={inputCls}
                      type={f.type === 'number' ? 'number' : 'text'}
                      placeholder={f.placeholder}
                      value={values[f.name] ?? ''}
                      onChange={e => set(f.name, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={send}
              disabled={loading}
              className="h-8 px-4 rounded-lg text-[12px] font-semibold transition-colors"
              style={{
                background: loading ? '#263044' : '#EDF0F7',
                color:      loading ? '#48566A'  : '#0B0E14',
              }}
            >
              {loading ? 'Sending...' : 'Send Request'}
            </button>
            {status !== null && (
              <div className="flex items-center gap-2">
                <span
                  className="font-mono text-[12px] font-semibold px-2 py-0.5 rounded"
                  style={{
                    color:      status >= 200 && status < 300 ? '#00D98B' : '#FF4060',
                    background: status >= 200 && status < 300 ? 'rgba(0,217,139,0.08)' : 'rgba(255,64,96,0.08)',
                  }}
                >
                  {status}
                </span>
                {elapsed !== null && <span className="font-mono text-[11px] text-ink-3">{elapsed}ms</span>}
              </div>
            )}
          </div>

          {response !== null && (
            <div className="rounded-lg overflow-hidden border border-border">
              <div className="px-3 py-2 flex items-center justify-between bg-bg border-b border-border">
                <span className="font-mono text-[10px] text-ink-3 uppercase tracking-widest">Response</span>
                <button
                  onClick={() => navigator.clipboard?.writeText(JSON.stringify(response, null, 2))}
                  className="font-mono text-[10px] text-ink-3 hover:text-ink-2 transition-colors"
                >
                  Copy
                </button>
              </div>
              <pre
                className="p-4 font-mono text-[12px] leading-relaxed overflow-auto max-h-80 bg-bg"
                dangerouslySetInnerHTML={{ __html: highlightJson(JSON.stringify(response, null, 2)) }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ApiPage() {
  return (
    <>
      <PageHeader title="API Explorer" />
      <div className="px-8 py-8 max-w-3xl">
        <p className="text-[13px] text-ink-2 mb-6">
          Live playground for all gateway endpoints. Requests go directly to{' '}
          <span className="font-mono text-[12px] text-ink-2 bg-surface px-1.5 py-0.5 rounded border border-border">{BASE}</span>
        </p>

        <div className="space-y-3">
          {ENDPOINTS.map(ep => <EndpointCard key={ep.path + ep.method} ep={ep} />)}
        </div>

        <div className="mt-6 px-4 py-3 rounded-xl bg-surface shadow-card">
          <p className="font-mono text-[11px] text-ink-3 leading-relaxed">
            Start the full stack with{' '}
            <span className="text-ink-2 font-medium">docker compose up --build</span>{' '}
            before sending requests. The ingestion service loads the 590k-row dataset into PostgreSQL on startup (2–3 min).
          </p>
        </div>
      </div>
    </>
  );
}
