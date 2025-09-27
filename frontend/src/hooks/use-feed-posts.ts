import { useQuery } from "@tanstack/react-query";

import { fetchPostsFeed } from "@/lib/api/posts";

interface UseFeedPostsOptions {
  limit?: number;
  offset?: number;
}

export function useFeedPosts(options?: UseFeedPostsOptions) {
  const limit = options?.limit;
  const offset = options?.offset;
  return useQuery({
    queryKey: ["feed", "posts", limit ?? "default", offset ?? 0],
    queryFn: () => fetchPostsFeed({ limit, offset }),
    select: (data) => data.results,
  });
}
