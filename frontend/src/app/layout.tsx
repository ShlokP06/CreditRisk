import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

const sans = Geist({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const mono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'CreditRisk — Fraud Intelligence Platform',
  description: 'Real-time transaction fraud scoring powered by XGBoost, SHAP explanations, and LLM-narrated alerts.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body className="bg-bg text-ink">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 min-h-screen ml-[220px]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
