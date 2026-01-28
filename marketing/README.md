# InvestEz Marketing Website

Marketing landing page for InvestEz - Portfolio consolidation + AI research for Indian retail investors.

## What InvestEz Solves

### Problem #1: Portfolio Consolidation
Your investments are scattered across multiple brokers (Zerodha, Groww, Upstox, etc.). InvestEz brings everything together in one unified dashboard. See all your stocks, mutual funds, and portfolios in one place.

### Problem #2: AI-Powered Research
Investment research is complex and jargon-heavy. InvestEz provides plain-language AI analysis and insights. Ask questions about your investments and get instant, easy-to-understand answers.

## Phase 1: Marketing Website (Current)

This implementation includes:
- Single scrollable landing page with all sections
- Sections: Hero, Features, How It Works, Pricing, About, Final CTA
- Responsive design (mobile, tablet, desktop)
- Smooth scroll navigation
- Sticky navbar with scroll effects
- Modern UI with Tailwind CSS
- SEO optimized for search engines and AI agents

## Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Lucide React (icons)
- React Helmet Async (SEO meta tags)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The site will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
marketing/
├── public/
│   ├── images/           # Images and assets
│   ├── favicon.svg       # Site favicon
│   ├── robots.txt        # SEO robots file
│   ├── sitemap.xml       # SEO sitemap
│   ├── humans.txt        # Human-readable site info
│   └── .well-known/      # AI agent discovery
│       ├── ai-plugin.json    # AI agent manifest
│       ├── site.json         # Structured site data
│       ├── openapi.json      # API specification
│       └── security.txt      # Security contact
├── src/
│   ├── components/
│   │   ├── layout/       # Navbar, Footer
│   │   ├── sections/     # All landing page sections
│   │   └── ui/           # Reusable UI components
│   ├── content/          # Static content (JSON)
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
└── package.json
```

## Features

### Smooth Scrolling
- Click navbar links to smoothly scroll to sections
- "Get Started" buttons scroll to pricing section
- All sections have proper scroll margin for fixed navbar

### Responsive Design
- Mobile-first approach
- Hamburger menu on mobile devices
- Stack layout on small screens
- Grid layout on larger screens

### SEO Optimized
- Meta tags for social sharing
- Sitemap and robots.txt
- AI agent discovery files
- Semantic HTML structure
- Fast page load times

## Future Phases

### Phase 2: Google OAuth Authentication
- Add user authentication
- Create user accounts
- Dashboard access for logged-in users

### Phase 3: Multi-Broker Integration
- Connect multiple broker accounts (Zerodha, Groww, Upstox)
- Consolidate portfolios from all platforms
- Real-time sync across brokers
- AI-powered insights on complete portfolio

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

Domain: https://investez.vercel.app

## Notes

- This is Phase 1: Marketing website only (no authentication)
- All "Get Started" buttons are placeholders for future functionality
- Images in `/public/images/` are placeholders (add real assets as needed)
- Supported brokers: Zerodha, Groww, Upstox (more coming soon)
