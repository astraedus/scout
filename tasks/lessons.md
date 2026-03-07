# Scout Project Lessons

## Next.js / Tailwind v4

### Tailwind v4 CSS syntax
- Uses `@import "tailwindcss"` not `@tailwind base/components/utilities` — these are v3 directives
- Custom CSS variables work fine alongside Tailwind classes
- No `tailwind.config.js` needed for basic usage; config inline in CSS with `@theme`

### App Router dynamic params
- In Next.js 16 (App Router), `params` is a Promise — must `use(params)` in client components or `await params` in server components
- Pattern: `const { id } = use(params)` where params is typed as `Promise<{ id: string }>`

### Build process
- `npx tsc --noEmit` first, then `npm run build` — catches type errors before spending time on the full build
- Next.js 16 uses Turbopack by default for builds

## API / SSE patterns
- EventSource `onerror` fires on any connection issue — use it to fall back to polling
- When backend is offline, `getHistory()` and `getResearch()` will throw — always catch and show empty state gracefully
