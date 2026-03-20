/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#FFFEF5',
          100: '#FFF9DB',
          200: '#FFF3B8',
          300: '#FFEB85',
          400: '#FFE04A',
          500: '#FDB813',
          600: '#E5A200',
          700: '#CC8F00',
        },
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
