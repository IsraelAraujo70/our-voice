# OUR Voice — Frontend

Interface web construída com Next.js + shadcn/ui, alinhada ao PRD da plataforma OUR Voice.

## Principais dependências

- Next.js 14 (App Router, TypeScript)
- Zustand para estado global leve (tabs do feed, preferências)
- React Query para cache de requisições à API
- shadcn/ui + Tailwind para os componentes de interface
- next-themes para alternância claro/escuro

## Scripts (via Bun)

```bash
bun install          # instala dependências
bun run dev          # http://localhost:3000
bun run build        # build de produção
bun run lint         # validação com ESLint
```

## Configuração

1. Crie `.env.local` a partir de `.env.local.example`.
2. Ajuste `NEXT_PUBLIC_API_BASE_URL` caso a API esteja em outro host.
3. Rode `bun install` seguido de `bun run dev`.

A página inicial (`src/app/page.tsx`) já contém componentes mockados para feed, votação popular e painel lateral. Substitua os dados estáticos conectando-se às rotas reais expostas pelo backend (`/api/posts`, `/api/votes`, etc.).

## Estrutura relevante

- `src/components/ui` — componentes base clonados do shadcn/ui.
- `src/components/feed` — composer, cards e tabs do feed.
- `src/lib/api-client.ts` — helper de fetch para a API Django.
- `src/stores/feed-store.ts` — stores Zustand (tabs/estado local).

Contribua adicionando testes (Vitest/RTL) e páginas adicionais conforme o roadmap (perfil, debates populares, transparência).
