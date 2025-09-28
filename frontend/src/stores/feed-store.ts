import { create } from "zustand"

export type FeedScope = "for_you" | "following"

interface FeedState {
  scope: FeedScope
}

interface FeedActions {
  setScope: (scope: FeedScope) => void
}

export const useFeedStore = create<FeedState & FeedActions>((set) => ({
  scope: "for_you",
  setScope: (scope) => set({ scope }),
}))
