/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        background: {
          light: '#f8fafc',
          dark: '#080c14',
        },
        surface: {
          light: '#ffffff',
          dark: '#0f172a',
          darker: '#0b0f19',
        },
        card: {
          light: '#ffffff',
          dark: '#111827',
        },
        border: {
          light: '#e2e8f0',
          dark: 'rgba(255, 255, 255, 0.08)',
        },
        accent: {
          cyan: '#06b6d4',
          blue: '#3b82f6',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
          violet: '#8b5cf6',
        }
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glow-cyan': '0 0 20px -5px rgba(6, 182, 212, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'scale-in': 'scaleIn 0.15s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        }
      }
    },
  },
  plugins: [],
}
