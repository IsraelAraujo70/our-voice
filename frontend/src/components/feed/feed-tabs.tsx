"use client";

import { useMemo } from "react";
import { Flame, History, UsersRound } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useFeedPosts } from "@/hooks/use-feed-posts";
import { mapPostToPostCard, type ApiPost } from "@/lib/api/posts";
import { useFeedStore } from "@/stores/feed-store";

import { PostCard } from "./post-card";

const tabItems = [
  { value: "following", label: "Seguindo", icon: UsersRound },
  { value: "popular", label: "Debates Populares", icon: Flame },
  { value: "archived", label: "Arquivados", icon: History },
] as const;

export function FeedTabs() {
  const { activeTab, setActiveTab } = useFeedStore();
  const {
    data: posts = [],
    isLoading,
    isError,
  } = useFeedPosts();

  const postsByTab = useMemo(() => {
    const computeScore = (post: ApiPost) =>
      (post.likes_count ?? 0) + (post.reposts_count ?? 0) + (post.replies_count ?? 0) + (post.votes_count ?? 0);
    const activePosts = posts.filter((post) => !post.is_archived);

    return {
      following: [...activePosts].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      ),
      popular: [...activePosts].sort((a, b) => {
        const scoreDiff = computeScore(b) - computeScore(a);
        if (scoreDiff !== 0) return scoreDiff;
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }),
      archived: posts
        .filter((post) => post.is_archived)
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
    } satisfies Record<typeof tabItems[number]["value"], ApiPost[]>;
  }, [posts]);

  const renderTabContent = (tabValue: typeof tabItems[number]["value"]) => {
    if (isLoading) {
      return <p className="text-sm text-muted-foreground">Carregando feed...</p>;
    }

    if (isError) {
      return <p className="text-sm text-destructive">Não foi possível carregar o feed agora.</p>;
    }

    const tabPosts = postsByTab[tabValue];

    if (!tabPosts?.length) {
      return <p className="text-sm text-muted-foreground">Nenhuma publicação disponível.</p>;
    }

    return tabPosts.map((post) => <PostCard key={post.id} {...mapPostToPostCard(post)} />);
  };

  return (
    <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as typeof tabItems[number]["value"])} className="space-y-4">
      <TabsList className="w-full justify-start">
        {tabItems.map(({ value, label, icon: Icon }) => (
          <TabsTrigger value={value} key={value} className="gap-2">
            <Icon className="h-4 w-4" />
            {label}
          </TabsTrigger>
        ))}
      </TabsList>
      {tabItems.map(({ value }) => (
        <TabsContent key={value} value={value} className="space-y-4">
          {activeTab === value ? renderTabContent(value) : null}
        </TabsContent>
      ))}
    </Tabs>
  );
}
