# PriceNest — Frontend Web Application

The PriceNest frontend is a modern web application built with **Next.js** and **TypeScript**, targeting deployment on **Vercel**. It provides an intuitive, responsive interface for property buyers, sellers, and investors in Pune, Maharashtra, to estimate real-estate prices, explore micro-market trends, and understand valuation drivers.

---

## 1. Directory Structure

```
frontend/
├── README.md               # Frontend architecture & developer guide (this file)
├── .env.example            # Template for environment configuration
├── package.json            # Node.js dependencies and build scripts (Phase 2+)
├── tsconfig.json           # TypeScript configuration
├── next.config.ts          # Next.js configuration
├── public/                 # Static assets, icons, and logos
│   └── .gitkeep
└── src/
    ├── app/                # Next.js App Router pages and layouts
    │   ├── layout.tsx      # Root layout (fonts, metadata, providers)
    │   ├── page.tsx        # Landing & valuation calculator page
    │   ├── auth/           # User authentication (login, register)
    │   │   ├── login/
    │   │   └── register/
    │   ├── history/        # Private user prediction history (PRD F-04)
    │   ├── explore/        # Pune locality & micro-market explorer
    │   └── methodology/    # Disclaimers, data provenance, and model docs
    ├── components/         # Reusable UI component library
    │   ├── ui/             # Core design system primitives (Button, Input, Card, Modal)
    │   ├── auth/           # Login/Register forms & auth guard components
    │   ├── calculator/     # Property valuation form & dynamic range slider
    │   ├── history/        # Private prediction history list & snapshot cards
    │   ├── results/        # Price estimate display, breakdown card, per-sqft metrics
    │   └── locality/       # Pune micro-market badge, locality selector & trends
    ├── lib/                # API client, utility functions, formatters
    │   ├── api.ts          # Typed HTTP client communicating with FastAPI backend
    │   └── formatters.ts   # Indian Rupee (INR Lakhs/Crores) & sq. ft. formatters
    ├── types/              # Shared TypeScript interfaces & API contract types
    │   ├── api.ts
    │   ├── auth.ts
    │   └── property.ts
    └── styles/             # Global CSS and design tokens
        └── globals.css
```


---

## 2. Technology Stack

- **Framework:** [Next.js](https://nextjs.org/) (App Router, Server & Client Components)
- **Language:** [TypeScript](https://www.typescriptlang.org/) (Strict typing throughout)
- **Styling:** Vanilla CSS / Tailwind CSS with modern design tokens (vibrant palette, dark mode support, glassmorphism)
- **Data Fetching:** Native `fetch` with server-side caching / React Query for client mutations
- **Deployment Platform:** [Vercel](https://vercel.com/) (Edge CDN, Serverless functions, automatic preview deployments)

---

## 3. Key User Experience Capabilities

1. **Intuitive Valuation Calculator:**
   - Multi-step or instant single-view input for Pune localities (e.g., Kothrud, Baner, Wakad, Viman Nagar, Kharadi, Hadapsar).
   - Real-time parameter controls for BHK, total area (sq. ft.), bathrooms, balconies, and property condition.
2. **Transparent Valuation Display:**
   - Primary valuation output in standard Indian currency denominations (₹ Lakhs and ₹ Crores).
   - Estimated price range / confidence band (e.g., ₹68.5L – ₹74.0L) to communicate market variance.
   - Estimated per-square-foot rate (₹/sq.ft.) with comparison against the locality benchmark.
3. **Prominent Data Provenance Disclaimers:**
   - High-visibility banner informing users of the development model's synthetic Kaggle dataset origin.
   - Explicit disclaimer that estimates are baseline algorithmic simulations and not certified government stamp duty or deed valuations.

---

## 4. Local Development Workflow (Reference)

*Note: Package installation and frontend initialization will take place in subsequent project phases.*

1. **Environment Setup:**
   ```bash
   cp frontend/.env.example frontend/.env.local
   # Ensure NEXT_PUBLIC_API_BASE_URL points to the FastAPI backend
   ```
2. **Install Dependencies (When ready):**
   ```bash
   cd frontend
   npm install
   ```
3. **Start Development Server:**
   ```bash
   npm run dev
   # Open http://localhost:3000 in your browser
   ```
4. **Build & Typecheck:**
   ```bash
   npm run build
   ```
