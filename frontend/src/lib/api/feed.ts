import { apiFetch } from "@/lib/api-client"
import type { PaginatedResponse, PostDto } from "@/types/post-types"

type FeedScope = "for_you" | "following"

interface FetchFeedParams {
  scope: FeedScope
  page?: number | string
}

export async function fetchFeed({ scope, page }: FetchFeedParams) {
  const searchParams = new URLSearchParams()
  if (scope) {
    searchParams.set("scope", scope)
  }
  if (page) {
    searchParams.set("page", String(page))
  }

  const queryString = searchParams.toString()
  const url = `/posts/feed/${queryString ? `?${queryString}` : ""}`
  return apiFetch<PaginatedResponse<PostDto>>(url)
}

export type { FeedScope }
