# SCFCA Frontend (React)

This frontend has been migrated in place from Streamlit to a React + TypeScript + Tailwind dashboard.

## Run locally

1. Install Node.js 20+ (includes npm).
2. From the repository root:

```bash
npm --prefix frontend install
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Default frontend URL: http://127.0.0.1:5173

Backend API base URL is configured as: http://127.0.0.1:8000

## Typecheck

```bash
npm --prefix frontend run typecheck
```

## Current structure

- src/app: app shell and routes
- src/layouts: dashboard layout
- src/components: reusable UI components
- src/pages: Login, Dashboard, Cases, Assets, Tickets, Audit, Documents, Account, Settings
- src/services: API and data services
- src/hooks: auth/session state
- src/types: shared TypeScript models