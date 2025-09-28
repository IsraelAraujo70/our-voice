"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useInfiniteQuery, type InfiniteData } from "@tanstack/react-query";
import { AuthModal } from "@/components/auth/auth-modal";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { buildWebSocketUrl } from "@/lib/api-client";
import { fetchFeed, type FeedScope } from "@/lib/api/feed";
import { useAuth } from "@/hooks/use-auth";
import { useFeedStore } from "@/stores/feed-store";
import type { PaginatedResponse, PostDto } from "@/types/post-types";
import { FeedItem } from "./feed-item";

interface BaseFeedMessage {
  scope: FeedScope;
}

interface FeedInitialMessage extends BaseFeedMessage {
  type: "feed.initial" | "feed.snapshot";
  posts: PostDto[];
}

interface FeedUpdateMessage extends BaseFeedMessage {
  type: "feed.update";
  event: string;
  post: PostDto;
}

type FeedMessage = FeedInitialMessage | FeedUpdateMessage;

const FEED_QUERY_KEY = (scope: FeedScope) => ["feed", scope] as const;

function extractNextPageParam(nextUrl: string | null): string | undefined {
  if (!nextUrl) return undefined;
  try {
    const url = new URL(nextUrl, typeof window === "undefined" ? "http://localhost" : window.location.origin);
    return url.searchParams.get("page") ?? undefined;
  } catch {
    return undefined;
  }
}

export function RealtimeFeed() {
  const { scope } = useFeedStore();
  const setScope = useFeedStore((state) => state.setScope);
  const { token, isAuthenticated } = useAuth();
  const isUserAuthenticated = isAuthenticated();
  const [livePosts, setLivePosts] = useState<PostDto[]>([]);
  const [socketError, setSocketError] = useState<string | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const shouldRequireAuth = scope === "following" && !isUserAuthenticated;

  const {
    data,
    isLoading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery<
    PaginatedResponse<PostDto>,
    Error,
    InfiniteData<PaginatedResponse<PostDto>, number | string>,
    readonly ["feed", FeedScope],
    number | string
  >({
    queryKey: FEED_QUERY_KEY(scope),
    initialPageParam: 1,
    queryFn: ({ pageParam }) => fetchFeed({ scope, page: pageParam }),
    getNextPageParam: (lastPage) => extractNextPageParam(lastPage.next),
    enabled: !shouldRequireAuth,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    setLivePosts([]);
    setSocketError(null);
  }, [scope]);

  useEffect(() => {
    if (shouldRequireAuth) {
      return;
    }

    let disposed = false;

    const websocketUrl = buildWebSocketUrl("/ws/posts/feed/", {
      scope,
      token: scope === "following" ? token ?? undefined : undefined,
    });

    const socket = new WebSocket(websocketUrl);

    socket.onopen = () => {
      setSocketError(null);
    };

    socket.onmessage = (event) => {
      try {
        const message: FeedMessage = JSON.parse(event.data);
        if (message.scope !== scope) {
          return;
        }
        setSocketError(null);
        if (message.type === "feed.initial" || message.type === "feed.snapshot") {
          setLivePosts(message.posts);
        } else if (message.type === "feed.update") {
          setLivePosts((prev) => {
            if (prev.some((item) => item.id === message.post.id)) {
              return prev;
            }
            return [message.post, ...prev].slice(0, 100);
          });
        }
      } catch (wsError) {
        console.error("Failed to parse websocket message", wsError);
      }
    };

    socket.onerror = () => {
      setSocketError("Não foi possível manter a conexão em tempo real. Tentaremos novamente em instantes.");
    };

    socket.onclose = (event) => {
      if (!disposed && event.code !== 1000 && !shouldRequireAuth) {
        setSocketError("Não foi possível manter a conexão em tempo real. Tentaremos novamente em instantes.");
      }
    };

    return () => {
      disposed = true;
      socket.close();
    };
  }, [scope, token, shouldRequireAuth]);

  useEffect(() => {
    const container = scrollContainerRef.current;
    const sentinel = sentinelRef.current;
    if (!container || !sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      {
        root: container,
        threshold: 1,
      }
    );

    observer.observe(sentinel);

    return () => {
      observer.disconnect();
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage, data]);

  const combinedPosts = useMemo(() => {
    const seen = new Set<number>();
    const ordered: PostDto[] = [];

    for (const post of livePosts) {
      if (!seen.has(post.id)) {
        seen.add(post.id);
        ordered.push(post);
      }
    }

    const queryPosts = data?.pages.flatMap((page) => page.results) ?? [];
    for (const post of queryPosts) {
      if (!seen.has(post.id)) {
        seen.add(post.id);
        ordered.push(post);
      }
    }

    return ordered;
  }, [livePosts, data]);

  if (shouldRequireAuth) {
    return (
      <GlassCard className="p-8 text-center space-y-4">
        <h3 className="text-xl font-semibold" style={{ color: "var(--c-content)" }}>
          Faça login para ver quem você segue
        </h3>
        <p className="text-sm" style={{ color: "color-mix(in srgb, var(--c-content) 70%, transparent)" }}>
          O feed Seguindo mostra apenas as novas postagens de perfis que você acompanha.
        </p>
        <AuthModal>
          <Button variant="secondary">Entrar ou criar conta</Button>
        </AuthModal>
        <Button variant="ghost" onClick={() => setScope("for_you")}>Ver feed público</Button>
      </GlassCard>
    );
  }

  if (isError) {
    return (
      <GlassCard className="p-8 text-center space-y-4">
        <h3 className="text-xl font-semibold" style={{ color: "var(--c-content)" }}>
          Não foi possível carregar o feed
        </h3>
        <p className="text-sm" style={{ color: "color-mix(in srgb, var(--c-content) 70%, transparent)" }}>
          {(error as Error)?.message ?? "Tente novamente em instantes."}
        </p>
        <Button onClick={() => void refetch()} variant="secondary">
          Tentar novamente
        </Button>
      </GlassCard>
    );
  }

  const isEmpty = !isLoading && combinedPosts.length === 0;

  return (
    <div className="space-y-4">
      {socketError && (
        <GlassCard className="p-3 text-sm" style={{ color: "color-mix(in srgb, var(--c-content) 80%, transparent)" }}>
          {socketError}
        </GlassCard>
      )}
      <div
        ref={scrollContainerRef}
        className="max-h-[70vh] overflow-y-auto pr-1 space-y-4"
      >
        {isLoading && combinedPosts.length === 0 ? (
          <FeedLoadingState />
        ) : isEmpty ? (
          <GlassCard className="p-8 text-center" style={{ color: "color-mix(in srgb, var(--c-content) 75%, transparent)" }}>
            Nenhuma postagem encontrada ainda.
          </GlassCard>
        ) : (
          combinedPosts.map((post) => <FeedItem key={post.id} post={post} />)
        )}
        <div ref={sentinelRef} />
        {isFetchingNextPage && (
          <GlassCard className="p-4 text-center text-sm" style={{ color: "color-mix(in srgb, var(--c-content) 70%, transparent)" }}>
            Carregando mais postagens...
          </GlassCard>
        )}
        {!hasNextPage && combinedPosts.length > 0 && (
          <GlassCard className="p-4 text-center text-xs" style={{ color: "color-mix(in srgb, var(--c-content) 60%, transparent)" }}>
            Você chegou ao fim por enquanto.
          </GlassCard>
        )}
      </div>
    </div>
  );
}

function FeedLoadingState() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, index) => (
        <GlassCard key={index} className="p-4 animate-pulse space-y-3">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-white/10" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-1/3 rounded bg-white/10" />
              <div className="h-3 w-1/5 rounded bg-white/5" />
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-3 w-full rounded bg-white/10" />
            <div className="h-3 w-5/6 rounded bg-white/10" />
          </div>
        </GlassCard>
      ))}
    </div>
  );
}
