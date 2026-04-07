/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        main: '#0B0914',
        surface: '#151123',
        'border-subtle': '#241B3B',
        accent: '#8B5CF6',
        'accent-hover': '#7C3AED',
        critical: '#EF4444',
        warning: '#F59E0B',
        success: '#10B981',
        'text-primary': '#F8F5FF',
        'text-secondary': '#A594C6'
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(15px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards',
      }
    },
  },
  plugins: [],
}