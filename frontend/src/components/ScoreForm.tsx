'use client';
import { useState } from 'react';
import { scoreEnriched } from '@/lib/api';
import type { ScoreResult } from '@/lib/types';

interface Props {
  onSubmit: (fn: () => Promise<ScoreResult>) => void;
  loading: boolean;
}

const BRANDS   = [['visa','Visa'],['mastercard','Mastercard'],['american express','Amex'],['discover','Discover']];
const TYPES    = [['credit','Credit'],['debit','Debit']];
const PRODUCTS = [['W','W — Goods'],['H','H — Hotel'],['C','C — Cash'],['S','S — Service'],['R','R — Refund']];
const DEVICES  = [['unknown','Unknown'],['desktop','Desktop'],['mobile','Mobile']];

const field = 'w-full h-10 px-3 rounded-lg bg-surface border border-border-strong text-ink text-[13px] outline-none focus:border-border-strong placeholder:text-ink-3';
const lbl   = 'block font-mono text-[10px] uppercase tracking-widest text-ink-3 mb-1.5';

export function ScoreForm({ onSubmit, loading }: Props) {
  const [userId,  setUserId]  = useState('');
  const [amount,  setAmount]  = useState('');
  const [brand,   setBrand]   = useState('visa');
  const [type,    setType]    = useState('credit');
  const [product, setProduct] = useState('W');
  const [device,  setDevice]  = useState('unknown');

  const valid = userId.trim().length > 0 && Number(amount) > 0;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!valid) return;
    onSubmit(() => scoreEnriched({
      user_id: userId.trim(),
      amount: parseFloat(amount),
      card_brand: brand,
      card_type: type,
      product_cd: product,
      device_type: device,
    }));
  };

  return (
    <form onSubmit={submit} className="space-y-5">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={lbl}>Card ID <span className="text-ink-2">*</span></label>
          <input
            className={field}
            placeholder="e.g. 13926"
            value={userId}
            onChange={e => setUserId(e.target.value)}
            required
          />
        </div>
        <div>
          <label className={lbl}>Amount USD <span className="text-ink-2">*</span></label>
          <input
            className={`${field} font-mono`}
            type="number"
            step="0.01"
            min="0.01"
            placeholder="250.00"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            required
          />
        </div>
      </div>

      <div>
        <p className="font-mono text-[10px] uppercase tracking-widest text-ink-3 mb-2">Optional</p>
        <div className="grid grid-cols-2 gap-3">
          {([
            [brand, setBrand, BRANDS, 'Card Brand'],
            [type, setType, TYPES, 'Type'],
            [product, setProduct, PRODUCTS, 'Product'],
            [device, setDevice, DEVICES, 'Device'],
          ] as [string, (v: string) => void, string[][], string][]).map(([val, set, opts, name]) => (
            <div key={name}>
              <label className={lbl}>{name}</label>
              <select
                className={field}
                value={val}
                onChange={e => set(e.target.value)}
                style={{ backgroundImage: 'none' }}
              >
                {opts.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-1 flex items-center justify-between">
        <span className="font-mono text-[11px] text-ink-3">17 fields auto-enriched</span>
        <button
          type="submit"
          disabled={loading || !valid}
          className="h-9 px-5 rounded-lg text-[13px] font-semibold transition-colors"
          style={{
            background: loading || !valid ? '#263044' : '#EDF0F7',
            color:      loading || !valid ? '#48566A'  : '#0B0E14',
            cursor:     loading || !valid ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Scoring...' : 'Analyze →'}
        </button>
      </div>
    </form>
  );
}
