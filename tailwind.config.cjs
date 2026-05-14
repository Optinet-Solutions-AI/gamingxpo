/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0A0B',
        fg: '#F5F4F1',
        accent: '#E6FF3D',
        muted: '#A1A09B',
        line: '#1E1E20',
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        display: ['"Inter Tight"', '"Inter"', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display-xl': ['clamp(3rem, 6vw, 6rem)', { lineHeight: '0.95', letterSpacing: '-0.02em' }],
        'display-lg': ['clamp(2.25rem, 4vw, 4rem)', { lineHeight: '1.0', letterSpacing: '-0.02em' }],
        'display-md': ['clamp(1.5rem, 2.5vw, 2.25rem)', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
        body: ['1.125rem', { lineHeight: '1.6' }],
      },
      maxWidth: { prose: '65ch', layout: '1440px' },
      spacing: { section: '6rem', 'section-sm': '3rem' },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
