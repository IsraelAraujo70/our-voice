# OUR Voice

Rede social democrática com moderação comunitária, seguindo o [PRD](PRD.md). O projeto é dividido entre um backend em **Django/DRF** e um frontend em **Next.js (React) + shadcn/ui**, com banco PostgreSQL e Redis para filas e votos em tempo real.

## Stack principal

- Frontend: Next.js 14 (App Router, TypeScript), Tailwind + shadcn/ui, Zustand, React Query.
- Backend: Django 5 + DRF, Channels, Celery, PostgreSQL, Redis.
- Infra local: Docker Compose (Postgres, Redis, API, Web).
- Gerenciador de tarefas: [Bun](https://bun.sh) via `package.json` na raiz.

## Estrutura do repositório

```
our-voice/
├── PRD.md
├── README.md
├── docker-compose.yml
├── package.json          # scripts com Bun (backend/frontend/dev)
├── backend/
│   ├── config/            # Projeto Django (ASGI, Celery, REST setup)
│   ├── apps/              # Domínios: accounts, posts, moderation, interactions, notifications
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── manage.py
│   └── Dockerfile
└── frontend/
    ├── src/app/           # Next.js App Router + shadcn/ui
    ├── src/components/    # UI e componentes de feed
    ├── src/lib/           # QueryClient, API helpers
    ├── src/stores/        # Zustand stores
    ├── package.json
    └── Dockerfile
```

## Scripts com Bun

Instale o Bun globalmente (`curl -fsSL https://bun.sh/install | bash`) se ainda não tiver.

```bash
bun run backend:install   # instala dependências Python com uv
bun run backend:migrate   # aplica migrações (usa SQLite local por padrão)
bun run backend:check     # checagem Django
bun run frontend:install  # instala dependências do Next.js com bun install
bun run frontend:dev      # roda o frontend em http://localhost:3000
bun run frontend:lint     # lint do frontend
bun run dev               # sobe o stack com docker compose (Postgres, Redis, API e Web)
```

## Rodando com Docker

```bash
bun run dev
```

- API Django: http://localhost:8000/api/
- Frontend: http://localhost:3000
- Redis: tcp://localhost:6379
- PostgreSQL: postgresql://our_voice:our_voice@localhost:5432/our_voice

A primeira subida instala dependências nas imagens. Alterações locais são refletidas graças aos volumes montados.

### Override de desenvolvimento

O arquivo `docker-compose.override.yml` é carregado automaticamente pelo Docker Compose e adiciona:

- Montagem do código local no backend/frontend.
- Execução de migrações antes de subir o servidor Django.
- Serviços opcionais `celery` e `celery-beat` para processamento assíncrono.
- Exposição das portas do Postgres e Redis para uso em outras ferramentas locais.

Caso não deseje os serviços extras, rode `docker compose -f docker-compose.yml up` explicitamente.

## Setup manual (sem Docker)

### Backend

```bash
uv --version >/dev/null 2>&1 || curl -fsSL https://astral.sh/uv/install.sh | bash
cd backend
uv sync
cp .env.example .env  # ajuste credenciais conforme necessário

# para desenvolvimento rápido é possível usar SQLite
DJANGO_DB_ENGINE=django.db.backends.sqlite3 uv run python manage.py migrate
uv run python manage.py runserver
```

Variáveis relevantes (`.env`):

```
DJANGO_SECRET_KEY=...
POSTGRES_DB=our_voice
POSTGRES_USER=our_voice
POSTGRES_PASSWORD=our_voice
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Frontend

```bash
cd frontend
bun install
cp .env.local.example .env.local
bun run dev
```

O frontend espera a API em `NEXT_PUBLIC_API_BASE_URL` (padrão: `http://localhost:8000/api`).

## Scripts úteis adicionais

- `bun run frontend:lint` — validação do frontend.
- `bun run backend:check` — checagens do Django (`DJANGO_DB_ENGINE=django.db.backends.sqlite3` em ambientes sem Postgres).
- `uv run celery -A config worker -l info` — worker de filas (requer Redis).

## Próximos passos sugeridos

1. Implementar autenticação JWT + refresh no backend (`SimpleJWT`).
2. Criar consumidores WebSocket para feed em tempo real e notificações.
3. Conectar frontend às rotas reais da API usando React Query.
4. Adicionar testes automatizados (pytest + React Testing Library).

Sinta-se à vontade para evoluir o setup conforme o roadmap descrito no PRD.
