"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";
import { useFeedStore, type FeedScope } from "@/stores/feed-store";

const OPTIONS: Array<{ value: FeedScope; label: string }> = [
  {
    value: "for_you",
    label: "For you",
  },
  {
    value: "following",
    label: "Following",
  },
];

export function FeedScopeSwitcher() {
  const scope = useFeedStore((state) => state.scope);
  const setScope = useFeedStore((state) => state.setScope);

  const activeIndex = useMemo(
    () => OPTIONS.findIndex((option) => option.value === scope),
    [scope]
  );

  return (
    <fieldset className="w-full max-w-xs">
      <legend className="sr-only">Selecione o tipo de feed</legend>
      <div className="relative glass-card flex items-center rounded-full p-1">
        <span
          aria-hidden
          className="absolute inset-y-1 w-1/2 rounded-full bg-white/15 shadow-[0_6px_18px_rgba(0,0,0,0.25)] transition-transform duration-300"
          style={{ transform: `translateX(${activeIndex * 100}%)` }}
        />
        {OPTIONS.map((option) => {
          const isActive = scope === option.value;
          return (
            <label
              key={option.value}
              className={cn(
                "relative z-10 flex-1 cursor-pointer select-none rounded-full px-3 py-2 text-center text-sm font-medium transition-colors",
                isActive
                  ? "text-white"
                  : "text-white/70 hover:text-white"
              )}
            >
              {option.label}
              <input
                className="sr-only"
                type="radio"
                name="feed-scope"
                value={option.value}
                checked={isActive}
                onChange={() => setScope(option.value)}
              />
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
