# Claude Code Guide - OUR Voice

## Visao Geral
- OUR Voice e uma rede social com moderacao comunitaria composta por backend Django/DRF e frontend Next.js (App Router) com shadcn/ui.
- O PRD principal esta em `PRD.md`; o README raiz detalha setup, scripts e arquitetura local.
- Banco primario PostgreSQL, Redis para filas e contagem de votos, Celery para processamento assincrono, Channels para WebSockets.
- **Ambiente dockerizado**: SEMPRE usar `docker exec` para comandos de instalacao, testes e execucao.

## Artefatos Essenciais
- `PRD.md`: visao de produto, escopo do MVP, requisitos funcionais e experiencia esperada.
- `README.md`: scripts Bun, estrutura do repo, stacks e instrucoes de setup com e sem Docker.
- `backend/README.md`: detalhes operacionais do Django, variaveis `.env`, comandos Celery.
- `frontend/README.md`: fluxo Next.js, dependencia de React Query. **NUNCA usar dados mock no frontend**.
- `docker-compose.yml` + `docker-compose.override.yml`: definem stack local (Postgres, Redis, API, Web, Celery opcional).

## Agentes e Responsabilidades

### Product Agent
- Mantem o PRD alinhado com roadmap e valida requisitos antes de cada iteracao.
- Define metrica de sucesso (ex: percentual de posts arquivados, engajamento dos debates) e garante rastreabilidade.
- Alinha regras de moderacao comunitaria e comunica mudancas aos demais agentes.

### Frontend Agent
- Local de trabalho: `frontend/src`. Padrao Next.js 14 com App Router e componentes shadcn/ui.
- Estado global leve via Zustand (`src/stores`) e cache de dados via React Query (`src/lib/query-client.ts`).
- API helper central: `src/lib/api-client.ts` (usa `NEXT_PUBLIC_API_BASE_URL`). Novos endpoints devem ter modules dedicados em `src/lib/api/`.
- Components do feed em `src/components/feed/`; pagina inicial `src/app/page.tsx` consome feed e sugestoes de usuarios.
- **Boas praticas obrigatorias**:
  - **NUNCA usar dados mock** - sempre consumir APIs reais
  - **SEMPRE usar Bun** ao inves de npm: `docker exec our-voice_frontend_1 bun install`
  - **SEMPRE escrever testes unitarios** para novos componentes
  - **SEMPRE usar docker exec** para comandos: `docker exec our-voice_frontend_1 bun run lint`
  - Sempre tratar estados loading/erro, manter componentes `use client` apenas quando necessario
  - **SEMPRE usar MCP Context7** para documentacao de pacotes externos antes de instalar

### Backend Agent
- Local de trabalho: `backend/`. Projeto Django modular em `apps/` (`accounts`, `posts`, `moderation`, `interactions`, `notifications`).
- API exposta via DRF router (`config/api_router.py`); seguir convencao REST e viewsets.
- Autenticacao atual com TokenAuth; roadmap inclui JWT (SimpleJWT).
- Modelos centrais:
  - `apps/posts/models.py` para posts (arquivamento via `archive`).
  - `apps/moderation/models.py` para votos e decisoes.
  - `apps/interactions/models.py` para likes, reposts, bookmarks, replies.
- **Boas praticas obrigatorias**:
  - **SEMPRE usar UV** ao inves de pip: `docker exec our-voice_backend_1 uv pip install`
  - **SEMPRE escrever testes unitarios** para endpoints e viewsets
  - **SEMPRE usar docker exec** para comandos: `docker exec our-voice_backend_1 uv run pytest`
  - **SEMPRE usar MCP Context7** para documentacao de pacotes Python externos
  - **SEMPRE deixar mensagens da API em ingles** para consistencia
  - Ao criar endpoints, prover serializers dedicados e atualizar testes unitarios (pytest ou Django TestCase)

### DevOps Agent
- Mantem definicoes do Docker Compose e garante que override local reflita necessidades de desenvolvimento.
- Supervisiona variaveis sensiveis (`backend/.env`, `frontend/.env.local`) e integra com Secrets Manager em ambientes cloud futuros.
- Responsavel por pipelines (GitHub Actions referenciado no PRD) e provisionamento para ECS Fargate + CloudFront.
- Para novas deps infra, atualizar scripts `package.json` raiz e documentar no README.

### QA Agent
- Configura suites de testes: pytest + coverage no backend; React Testing Library + Vitest/Playwright no frontend.
- Define checklists de regressao focando em votacao popular, arquivamento de posts e fluxo de autenticacao.
- Monitora indicadores (ex: tempo medio de decisao de moderacao) e valida metricas do PRD.
- Automatiza lint/test no CI antes de merges.

## Boas Praticas Obrigatorias (Claude Code)

### Instalacao de Pacotes

1. **SEMPRE consultar MCP Context7** antes de instalar qualquer pacote externo
2. **Frontend**: usar `docker exec our-voice_frontend_1 bun add <package>`
3. **Backend**: usar `docker exec our-voice_backend_1 uv pip install <package>`

### Testes

1. **SEMPRE escrever testes unitarios** para novos componentes/endpoints
2. **Frontend**: `docker exec our-voice_frontend_1 bun run test`
3. **Backend**: `docker exec our-voice_backend_1 uv run pytest`

### Dados

1. **NUNCA usar dados mock no frontend** - sempre consumir APIs reais
2. **SEMPRE deixar mensagens da API em ingles**

### Comandos Docker

1. **SEMPRE usar docker exec** para todos os comandos de desenvolvimento
2. **NUNCA rodar comandos diretamente** no host para este projeto

## Fluxo de Trabalho Colaborativo

- Iniciar tarefas lendo `PRD.md` para entender contexto e restricoes.
- Abrir branch por feature; ao sincronizar, rodar scripts de validacao (lint/test) antes do PR.
- Usar React Query e endpoints DRF para eliminar mocks. Alteracoes no backend devem expor dados agregados (contadores de interacao) esperados pelo frontend.
- Documentar novas APIs ou processos diretamente no README relevante e referenciar em `agents.md`.

## Checklist Rapido por Entrega

- **Product**: requisitos atualizados? criterios de aceitacao claros?
- **Frontend**: componentes sem mocks, testes unitarios, estados handled, lint ok.
- **Backend**: endpoint coberto por testes, serializer/perms revisados, migracoes aplicaveis.
- **DevOps**: containers sobem com `bun run dev`, envs documentados.
- **QA**: testes automatizados passam, cobertura minima acordada atingida.

## Contatos e Escalada

- Product Agent: definir roadmap trimestral e aprovar mudancas de escopo.
- Tech Lead (coordena Frontend + Backend): resolve bloqueios tecnicos e garante alinhamento de arquitetura.
- DevOps Lead: responde por incidentes em staging/producao.
- QA Lead: gatekeeper de qualidade antes de releases.
- Em ausencia de um agente especifico, o time deve sinalizar no canal #our-voice e atualizar este documento.
- deixe as mensagens do retorno da api sempre em ingles por favor.