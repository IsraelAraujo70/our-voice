import { apiFetch, resolveMediaUrl } from "@/lib/api-client";
import type { PaginatedResponse } from "@/lib/api/posts";

export interface ApiUserProfile {
  location?: string | null;
  website?: string | null;
  pronouns?: string | null;
  updated_at?: string;
}

export interface ApiUser {
  id: number;
  email: string;
  handle: string;
  display_name: string;
  bio?: string;
  avatar?: string | null;
  banner?: string | null;
  reputation_score?: string | number;
  created_at: string;
  profile?: ApiUserProfile | null;
}

interface FetchUsersParams {
  limit?: number;
  offset?: number;
}

export async function fetchUsers(params?: FetchUsersParams) {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  const query = searchParams.toString();
  const path = `/users/${query ? `?${query}` : ""}`;
  return apiFetch<PaginatedResponse<ApiUser>>(path);
}

export interface SuggestedProfile {
  handle: string;
  displayName: string;
  avatarUrl?: string;
}

export function mapUserToSuggestedProfile(user: ApiUser): SuggestedProfile {
  return {
    handle: user.handle,
    displayName: user.display_name || user.handle,
    avatarUrl: resolveMediaUrl(user.avatar) ?? undefined,
  };
}
