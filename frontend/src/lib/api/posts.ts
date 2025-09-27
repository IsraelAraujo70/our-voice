import { PostCardProps } from "@/components/feed/post-card";
import { apiFetch, resolveMediaUrl } from "@/lib/api-client";

export interface ApiAuthor {
  id: number;
  handle: string;
  display_name: string;
  bio?: string | null;
  avatar?: string | null;
}

export interface ApiPost {
  id: number;
  author?: ApiAuthor | null;
  text: string;
  image?: string | null;
  visibility: string;
  in_reply_to?: number | null;
  quoted_post?: number | null;
  is_archived: boolean;
  archived_at?: string | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  likes_count?: number;
  replies_count?: number;
  reposts_count?: number;
  votes_count?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface FeedParams {
  limit?: number;
  offset?: number;
}

export async function fetchPostsFeed(params?: FeedParams) {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const query = searchParams.toString();
  const path = `/posts/feed/${query ? `?${query}` : ""}`;
  return apiFetch<PaginatedResponse<ApiPost>>(path);
}

const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
});

export function mapPostToPostCard(post: ApiPost): PostCardProps {
  const displayName = post.author?.display_name ?? "Membro anônimo";
  const handle = post.author?.handle ?? "anonimo";

  return {
    author: {
      handle,
      displayName,
      avatarUrl: resolveMediaUrl(post.author?.avatar) ?? undefined,
    },
    createdAt: dateFormatter.format(new Date(post.created_at)),
    text: post.text,
    imageUrl: resolveMediaUrl(post.image) ?? undefined,
    counts: {
      likes: post.likes_count ?? 0,
      replies: post.replies_count ?? 0,
      reposts: post.reposts_count ?? 0,
      votes: post.votes_count ?? 0,
    },
    archived: post.is_archived,
  };
}
