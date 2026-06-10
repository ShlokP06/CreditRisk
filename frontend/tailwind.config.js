/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:              '#0B0E14',
        surface:         '#111520',
        'surface-2':     '#171C2A',
        border:          '#1D2433',
        'border-strong': '#263044',
        ink:             '#EDF0F7',
        'ink-2':         '#7A8BA0',
        'ink-3':         '#48566A',
        safe:            '#00D98B',
        caution:         '#F0A428',
        threat:          '#FF4060',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      boxShadow: {
        card:    '0 0 0 1px #1D2433, 0 2px 12px rgba(0,0,0,0.4)',
        'card-md': '0 0 0 1px #263044, 0 4px 20px rgba(0,0,0,0.5)',
      },
    },
  },
  plugins: [],
};
