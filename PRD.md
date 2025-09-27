# PRD — OUR Voice (React + shadcn/ui • Django + PostgreSQL)

> **Resumo**: Este documento define a visão, escopo, requisitos funcionais e não funcionais, arquitetura, modelo de dados, APIs, UX e métricas da rede social **OUR Voice**, uma plataforma democrática e livre inspirada no conceito de microblog tipo Twitter/X, mas com **moderação feita pelo povo**. O frontend será em **React** com **shadcn/ui**, e o backend em **Django** + **PostgreSQL**. O objetivo é permitir **debates livres, abertos e responsáveis**, onde o controle do conteúdo é descentralizado e coletivo.

---

## 1) Visão & Propósito

* **Nome do Projeto**: OUR Voice

* **Missão**: Dar voz ao povo, permitindo debates livres e responsáveis sem censura centralizada. A moderação é feita pela comunidade: cada usuário decide o que quer ver ou não.

* **Valores**:

  * Liberdade de expressão.
  * Respeito mútuo e diálogo aberto.
  * Responsabilidade coletiva sobre o conteúdo.
  * Transparência e participação.

* **Slogan**: “A voz é nossa.”

---

## 2) Filosofia de Moderação

OUR Voice substitui a moderação tradicional por um **sistema de voto popular**.

* **Cada usuário** pode votar em um conteúdo que considera **danoso** (ex: violência, spam, discurso de ódio etc.).
* Quando o usuário **vota para remover**, o conteúdo **deixa de aparecer apenas para ele**.
* Se um número suficiente de usuários também votar, o conteúdo é **automaticamente ocultado globalmente** (removido do feed público e arquivado).
* Usuários podem **debater livremente ideias opostas**, sem risco de banimento por opinião.

### Tipos de Ações Comunitárias

1. **Votar para ocultar** → o conteúdo é removido só do feed pessoal.
2. **Votar para remover** → contribuição para a decisão coletiva.
3. **Debater** → responder ou citar o post com contra-argumento.

O sistema prioriza a **liberdade com responsabilidade**, permitindo que a comunidade mantenha o espaço saudável sem censura institucional.

---

## 3) Escopo do MVP

### Incluído

* Criação e autenticação de contas.
* Postagem de textos (até 500 caracteres) e imagens (1 por post).
* Feeds: Home (seguindo) e Perfil.
* Interações: like, reply, repost, bookmark.
* Votação de conteúdo (ocultar/remover).
* Busca de posts e usuários.
* Notificações (likes, replies, reposts, votos em posts próprios).
* Sistema de reputação básica (influência do voto aumenta conforme engajamento positivo do usuário).

### Fora do MVP

* DMs.
* Vídeos, GIFs, múltiplas imagens.
* Ranking de usuários ou gamificação.
* Feed personalizado (“Para você”).
* Comunidades/grupos.

---

## 4) Requisitos Funcionais

### 4.1 Autenticação

* E-mail + senha; login seguro via JWT com refresh tokens.
* Recuperação de senha por e-mail.

### 4.2 Postagens

* Texto até 500 caracteres.
* Upload opcional de imagem (jpg/png/webp, até 5MB).
* Reply, repost, quote, delete.
* Contadores de likes, reposts, replies e votos.

### 4.3 Votação Popular

* Botão **“Não quero ver”** → oculta post apenas para o usuário.
* Botão **“Votar para remover”** → registra voto coletivo.
* Quando um post atingir **X votos (ex: 5% dos visualizadores)** → é arquivado globalmente.
* O autor é notificado, mas não punido.
* Posts arquivados podem ser revisados em modo histórico (transparência pública).

### 4.4 Feed & Explorar

* Feed Home: posts recentes dos seguidos (ordem cronológica).
* Explorar: posts populares (mais interações, debates, votos e engajamento).

### 4.5 Perfil

* Bio, avatar, banner, handle único.
* Contadores de posts, seguidores e engajamentos.
* Histórico de debates (posts que o usuário respondeu ou votou).

### 4.6 Notificações

* Novo seguidor.
* Likes, replies, reposts, citações.
* Votos populares em posts próprios.

### 4.7 Debate

* Usuários podem responder com argumentos (“Debater”).
* As respostas com mais votos positivos (like/debate útil) sobem no ranking da discussão.

---

## 5) Requisitos Não Funcionais

* **Disponibilidade**: 99.5%.
* **Performance**: <300ms P95 nas rotas críticas.
* **Escalabilidade**: PostgreSQL + Redis + CDN.
* **Segurança**: cookies httpOnly, CSRF tokens, Argon2 hash.
* **Transparência**: histórico público de decisões de remoção.

---

## 6) Arquitetura Técnica

* **Frontend**: React + shadcn/ui + Zustand + React Query.
* **Backend**: Django + DRF + Channels (WebSocket) + Celery + Redis.
* **Banco**: PostgreSQL.
* **Gerenciador de dependências**: **uvx** (substituindo pip para isolamento, desempenho e consistência dos ambientes Python).
* **Storage**: AWS S3.
* **Infra**: ECS Fargate, CloudFront, Secrets Manager, GitHub Actions.

---

## 7) Modelo de Dados (Principais Tabelas)

* **users**(id, email, senha, data_criacao)
* **profiles**(user_id, handle, display_name, bio, avatar, banner)
* **posts**(id, autor_id, texto, imagem_url, created_at, deleted_at)
* **votes**(id, post_id, voter_id, type [‘ocultar’, ‘remover’], created_at)
* **likes**, **reposts**, **bookmarks**, **replies**, **notifications** (como no PRD anterior)

---

## 8) API

### Votos e Debates

* `PUT /api/posts/{id}/vote` → votar para ocultar ou remover.
* `GET /api/posts/{id}/votes` → estatísticas do post.
* `POST /api/posts/{id}/debate` → criar resposta ou contra-argumento.
* `GET /api/posts/{id}/debate` → listar discussões.

---

## 9) Lógica de Moderação Comunitária

* Cada voto é anônimo.
* Votos são ponderados pelo histórico de engajamento (usuários ativos têm peso maior).
* Quando a soma dos pesos ultrapassa o limiar (configurável via backend), o post é arquivado.
* O conteúdo arquivado **não é deletado**, mas movido para uma área de transparência pública (“Conteúdos arquivados”).

---

## 10) UX / UI (shadcn/ui)

* Layout minimalista, com cores neutras e ênfase em leitura.
* Botões de ação: Like ❤️, Repost ♻️, Debate 💬, Ocultar 🚫, Votar Remover ⚠️.
* Feedback visual claro para votos e debates.
* Página “Debates Populares” mostrando discussões ativas.

---

## 11) Métricas de Engajamento e Democracia

* % de posts com votos “remover”.
* Tempo médio de debate ativo.
* Taxa de engajamento vs. ocultamento.
* % de usuários que participam de debates.
* Distribuição dos tipos de votos (debate vs. ocultar vs. remover).

---

## 12) Roadmap (12 Semanas)

* **Sem 1–2**: Setup inicial, autenticação, perfis.
* **Sem 3–4**: CRUD posts, feeds.
* **Sem 5–6**: Sistema de votos populares.
* **Sem 7**: Debates (replies com destaque).
* **Sem 8–9**: Notificações e histórico de votos.
* **Sem 10**: Página de transparência (conteúdos arquivados).
* **Sem 11–12**: Testes, auditoria e lançamento beta.

---

## 13) Manifesto OUR Voice

> A voz é de todos. Ninguém deve calar o outro — mas também ninguém é obrigado a ouvir. Aqui, a comunidade decide o que deve permanecer visível. Cada voto, cada debate, cada palavra conta para construir um espaço digital verdadeiramente livre.
