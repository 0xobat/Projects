# val — Valentine's Day Webpage

A playful "Will you be my Valentine?" single-page app with premium dark aesthetic.

## Stack

- **Next.js 15** (App Router) with TypeScript
- **Tailwind CSS v4** with `@theme inline` for rose palette + navy gradients
- **Framer Motion** for entrance animations and floating hearts
- **Lucide React** for icons (Stars, Heart, ArrowDown)
- **Static export** (`output: "export"`) for Vercel deployment
- **Fonts**: Playfair Display (serif headings) + Inter (sans body) + Great Vibes (cursive accent) via `next/font`

## Structure

```
src/
  app/
    layout.tsx            — Root layout (fonts, metadata)
    page.tsx              — Assembles all sections + background effects
    globals.css           — Theme colors, keyframe animations, scrollbar
  components/
    FloatingHearts.tsx    — Framer Motion emoji hearts with sway (F006)
    HeroSection.tsx       — The Ask + dodging No button (F003 + F004)
    CelebrationModal.tsx  — Yes celebration orchestrator (F005)
    HeartBurst.tsx        — 3D heart particle burst (Three.js)
    VideoPlayer.tsx       — Celebration video player
    PhotoCarousel.tsx     — Our Memories carousel (F007)
    LoveLetter.tsx        — Word-by-word scroll reveal (F008)
    ScrollIndicator.tsx   — Bouncing arrow between hero and carousel
    Footer.tsx            — Simple footer (server component)
public/
  photos/                 — Personal photos + video
```

## Design Language

- **Background**: Navy/purple gradient (#0f0c29 → #302b63) with noise texture + ambient orbs
- **Color palette**: Rose (50–900) + pink/purple accents + white-with-opacity
- **Glass morphism**: bg-white/5-10, backdrop-blur, border-white/10
- **Typography**: Gradient clip text (rose-200 → rose-400), Great Vibes cursive for "Valentine?"
- **Animations**: Framer Motion whileInView, staggered entrances, text-glow, pulse-slow orbs

## Commands

```bash
pnpm dev        # Start dev server
pnpm build      # Production build (static export to out/)
pnpm lint       # ESLint check
```

## Personalization Needed

Before deploy, replace placeholder content:
1. **Hero subtitle** — in `HeroSection.tsx`, change the italic subtitle
2. **Love letter** — in `LoveLetter.tsx`, change `LETTER_TEXT`
3. **Celebration text** — in `CelebrationModal.tsx`, personalize the messages
4. **Photos** — add photos to `public/photos/` (currently 1-5.jpeg, New-year.jpeg, yes.jpeg)
5. **Photo captions** — update `PHOTOS` array in `PhotoCarousel.tsx`

## Agent Harness

This project uses the harness convention. See `harness/` directory:

- `harness/init.sh` — Install deps with pnpm
- `harness/verify.sh` — Run lint + build
- `harness/features.json` — Feature inventory with pass/fail status
- `harness/progress.txt` — Read this first to see what previous sessions did
