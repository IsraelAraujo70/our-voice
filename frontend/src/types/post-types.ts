export interface AuthorSummary {
  id: number
  handle: string
  display_name: string | null
  avatar: string | null
}

export type PostVisibility = "public" | "followers"

export interface PostDto {
  id: number
  author: AuthorSummary
  text: string
  image: string | null
  visibility: PostVisibility
  in_reply_to: number | null
  quoted_post: number | null
  is_archived: boolean
  archived_at: string | null
  deleted_at: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
