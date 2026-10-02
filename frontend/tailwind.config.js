/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        void: '#000000',
        surface: {
          1: '#0B0B0C',
          2: '#141416',
          3: '#1F1F23',
        },
        sentry: {
          emerald: '#00FF87',
          cyan: '#60EFFF',
          violet: '#8B5CF6',
          amber: '#F59E0B',
          red: '#EF4444',
          blue: '#38BDF8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
        display: ['"Space Grotesk"', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulseGlow 2.5s infinite ease-in-out',
        'pulse-slow': 'pulseSlow 3s infinite ease-in-out',
        'scanline': 'scanline 8s linear infinite',
        'float': 'float 4s ease-in-out infinite',
        'radar': 'radar 2s linear infinite',
        'shimmer': 'shimmer 2.5s infinite',
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'flow': 'flow 1.5s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', filter: 'drop-shadow(0 0 15px rgba(96, 239, 255, 0.3))' },
          '50%': { opacity: '0.8', filter: 'drop-shadow(0 0 25px rgba(0, 255, 135, 0.5))' },
        },
        pulseSlow: {
          '0%, 100%': { opacity: '0.8', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.02)' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        radar: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        flow: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      }
    },
  },
  plugins: [],
}
