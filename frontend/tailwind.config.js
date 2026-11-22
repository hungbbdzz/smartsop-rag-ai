/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          900: '#0c4a6e',
        },
        factory: {
          darkest: '#060a12',
          dark: '#090e17',
          panel: '#0b1329',
          card: '#0f172a',
          border: '#1e293b',
          accent: '#38bdf8',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'glow-blue': '0 0 25px -5px rgba(2, 132, 199, 0.45)',
        'glow-cyan': '0 0 15px -3px rgba(56, 189, 248, 0.35)',
        'glow-amber': '0 0 15px -3px rgba(245, 158, 11, 0.35)',
      },
    },
  },
  plugins: [],
};
