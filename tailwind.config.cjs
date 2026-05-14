/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F7F4EF',          // warm cream — main background
        'bg-alt': '#FFFFFF',    // white — alternating section break
        'bg-deep': '#1F1A14',   // dark espresso — for inverted sections (footer / contrast moments)
        fg: '#14110D',          // espresso ink — text
        muted: '#6E665A',       // warm gray
        line: '#E5E0D7',        // subtle border
        accent: '#F5C84B',      // amber gold — eyebrow text, highlights, accent moments
        ink: '#1A1A1A',         // near-black — for CTAs that need maximum contrast
        pop: '#E6FF3D',         // electric lime — sparing pops only (e.g. dot in logo)
        coral: '#E66B3D',       // warm coral — secondary accent for variation
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
      backgroundImage: {
        'grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.078 0 0 0 0 0.066 0 0 0 0 0.051 0 0 0 0.12 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
