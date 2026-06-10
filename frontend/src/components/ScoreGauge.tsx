'use client';
import { useEffect, useRef } from 'react';

interface Props { score: number; size?: number }

export function ScoreGauge({ score, size = 200 }: Props) {
  const circleRef = useRef<SVGCircleElement>(null);
  const numRef    = useRef<HTMLSpanElement>(null);

  const r            = 38;
  const circumference = 2 * Math.PI * r;
  const targetOffset  = circumference * (1 - score / 100);
  const color         = score < 33 ? '#00D98B' : score < 67 ? '#F0A428' : '#FF4060';

  useEffect(() => {
    const circle = circleRef.current;
    const num    = numRef.current;
    if (!circle || !num) return;

    circle.style.strokeDashoffset = String(circumference);
    const tCircle = setTimeout(() => {
      circle.style.transition = 'stroke-dashoffset 400ms cubic-bezier(0.22,1,0.36,1)';
      circle.style.strokeDashoffset = String(targetOffset);
    }, 60);

    const t0  = performance.now();
    const dur = 600;
    const tick = (now: number) => {
      const p = Math.min((now - t0) / dur, 1);
      const e = 1 - Math.pow(1 - p, 3);
      if (num) num.textContent = String(Math.round(score * e));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);

    return () => clearTimeout(tCircle);
  }, [score, circumference, targetOffset]);

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1D2433" strokeWidth="8" />
        <circle
          ref={circleRef}
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          ref={numRef}
          className="font-mono font-bold tabular-nums leading-none text-ink"
          style={{ fontSize: size * 0.28 }}
        >0</span>
        <span className="font-mono leading-none mt-1 text-ink-3" style={{ fontSize: size * 0.1 }}>/100</span>
      </div>
    </div>
  );
}
