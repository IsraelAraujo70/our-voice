# OUR Voice — Backend

Serviço Django/DRF responsável por autenticação, postagens, interações e moderação comunitária.

## Dependências principais

- Django 5.2 + Django REST Framework
- Channels + Daphne para WebSockets
- Celery + Redis para tarefas assíncronas e contagem de votos
- PostgreSQL como banco de dados primário

## Instalação local

Com Bun (scripts da raiz):

```bash
bun run backend:install
bun run backend:migrate    # usa SQLite por padrão
bun run backend:check
```

Ou manualmente (já dentro de `backend/`):

```bash
uv --version >/dev/null 2>&1 || curl -fsSL https://astral.sh/uv/install.sh | bash
uv sync
cp .env.example .env
uv run python manage.py migrate  # requer PostgreSQL ativo
uv run python manage.py runserver
```

Para desenvolvedores sem Postgres local, é possível usar SQLite temporariamente:

```bash
DJANGO_DB_ENGINE=django.db.backends.sqlite3 uv run python manage.py migrate
```

## Estrutura

- `config/` — settings, URLs, ASGI, Celery.
- `apps/accounts` — usuário customizado (`email` + `handle`) e perfis.
- `apps/posts` — modelo base de postagens (texto + imagem, replies, quote).
- `apps/interactions` — likes, reposts, bookmarks, replies.
- `apps/moderation` — votos populares e registro de decisões.
- `apps/notifications` — notificações de engajamento.

## Endpoints iniciais

- `POST /api/users/` — cria usuário (com senha).
- `GET /api/posts/` — lista posts (filtro `?author=`).
- `POST /api/posts/` — cria post autenticado.
- `POST /api/votes/` — registra voto (ocultar/remover) e avalia arquivamento.
- `GET /api/moderation-decisions/` — histórico de decisões.
- `POST /api/likes/`, `/api/replies/`, etc. — interações básicas.

Token de autenticação padrão via `POST /api/auth/token/`.

## Tarefas Celery

O arquivo `config/celery.py` configura a instância principal. Rode workers com:

```bash
uv run celery -A config worker -l info
```

## Próximos passos

- Adicionar JWT (SimpleJWT) e refresh tokens.
- Criar consumidores Channels para notificações em tempo real.
- Implementar política de reputação que afeta o peso dos votos.
