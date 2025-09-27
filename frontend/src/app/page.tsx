'use client';

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Flame, Shield, UserPlus } from "lucide-react";

import { FeedTabs } from "@/components/feed/feed-tabs";
import { ModerationBanner } from "@/components/feed/moderation-banner";
import { PostComposer } from "@/components/feed/post-composer";
import { SiteHeader } from "@/components/layout/site-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useFeedPosts } from "@/hooks/use-feed-posts";
import type { ApiPost } from "@/lib/api/posts";
import { fetchUsers, mapUserToSuggestedProfile } from "@/lib/api/users";

interface TrendingTag {
  tag: string;
  mentions: number;
}

function extractTrendingTags(posts: ApiPost[]): TrendingTag[] {
  if (!posts.length) return [];

  const counts = new Map<string, number>();

  const hashtagPattern = /#[\p{L}0-9_]+/gu;
  posts.forEach((post) => {
    const matches = post.text.match(hashtagPattern);
    if (!matches) return;
    matches
      .map((tag) => tag.toLowerCase())
      .forEach((tag) => counts.set(tag, (counts.get(tag) ?? 0) + 1));
  });

  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([tag, mentions]) => ({ tag, mentions }));
}

export default function Home() {
  const {
    data: feedPosts = [],
    isLoading: feedLoading,
  } = useFeedPosts();

  const {
    data: usersResponse,
    isLoading: usersLoading,
    isError: usersError,
  } = useQuery({
    queryKey: ["users", "suggested"],
    queryFn: () => fetchUsers({ limit: 5 }),
  });

  const trendingTags = useMemo(() => extractTrendingTags(feedPosts), [feedPosts]);

  const suggestedProfiles = useMemo(() => {
    if (!usersResponse?.results?.length) return [];
    return usersResponse.results.map(mapUserToSuggestedProfile);
  }, [usersResponse]);

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="mx-auto grid max-w-5xl gap-6 px-4 py-6 md:grid-cols-[2fr_1fr]">
        <section className="flex flex-col gap-4">
          <PostComposer />
          <ModerationBanner />
          <FeedTabs />
        </section>
        <aside className="space-y-4">
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="flex items-center gap-2 text-base">
                <Flame className="h-4 w-4 text-primary" />
                Tendências democráticas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {feedLoading ? (
                <p className="text-sm text-muted-foreground">Carregando tendências...</p>
              ) : trendingTags.length ? (
                trendingTags.map((item) => (
                  <div key={item.tag} className="flex items-center justify-between text-sm">
                    <div>
                      <p className="font-medium">{item.tag}</p>
                      <p className="text-muted-foreground">{item.mentions} menções recentes</p>
                    </div>
                    <Badge variant="outline">Debater</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Nenhum tema em alta no momento.</p>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="flex items-center gap-2 text-base">
                <UserPlus className="h-4 w-4 text-primary" />
                Quem seguir
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {usersLoading ? (
                <p className="text-sm text-muted-foreground">Buscando perfis para você...</p>
              ) : usersError ? (
                <p className="text-sm text-destructive">Não foi possível sugerir perfis agora.</p>
              ) : suggestedProfiles.length ? (
                suggestedProfiles.map((profile) => (
                  <div key={profile.handle} className="flex items-center justify-between text-sm">
                    <div>
                      <p className="font-medium">{profile.displayName}</p>
                      <p className="text-muted-foreground">@{profile.handle}</p>
                    </div>
                    <Badge variant="secondary">Seguir</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Sem sugestões disponíveis no momento.</p>
              )}
            </CardContent>
          </Card>
          <Card className="bg-muted/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Shield className="h-4 w-4 text-primary" />
                Transparência total
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              Todas as decisões de remoção ficam disponíveis no histórico público. Reivindique seu direito de saber como a comunidade vota.
            </CardContent>
          </Card>
        </aside>
      </main>
    </div>
  );
}
