import { create } from "zustand";

type FeedTab = "following" | "popular" | "archived";

interface FeedState {
  activeTab: FeedTab;
  setActiveTab: (tab: FeedTab) => void;
}

export const useFeedStore = create<FeedState>((set) => ({
  activeTab: "following",
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
