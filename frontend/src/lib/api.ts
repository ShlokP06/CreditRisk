import type { ScoreResult, AlertsResponse, HealthStatus } from './types';

const BASE = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8000';

export async function scoreEnriched(body: {
  user_id: string;
  amount: number;
  card_brand?: string;
  card_type?: string;
  product_cd?: string;
  device_type?: string;
}): Promise<ScoreResult> {
  const res = await fetch(`${BASE}/score-enriched`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getAlerts(limit = 50): Promise<AlertsResponse> {
  const res = await fetch(`${BASE}/alerts?limit=${limit}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${BASE}/health`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
