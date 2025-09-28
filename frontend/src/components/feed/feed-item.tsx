"use client";

import Image from "next/image";
import { GlassCard } from "@/components/ui/glass-card";
import { resolveMediaUrl } from "@/lib/api-client";
import type { PostDto } from "@/types/post-types";

interface FeedItemProps {
  post: PostDto;
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function FeedItem({ post }: FeedItemProps) {
  const displayName = post.author.display_name?.trim() || `@${post.author.handle}`;
  const avatarUrl = resolveMediaUrl(post.author.avatar);
  const imageUrl = resolveMediaUrl(post.image);

  return (
    <GlassCard className="p-4 space-y-4">
      <div className="flex items-start gap-3">
        {avatarUrl ? (
          <Image
            src={avatarUrl}
            alt={post.author.handle}
            width={48}
            height={48}
            className="h-12 w-12 rounded-full object-cover"
          />
        ) : (
          <div className="h-12 w-12 rounded-full bg-white/10 flex items-center justify-center text-sm font-semibold text-white/70">
            {post.author.handle.slice(0, 2).toUpperCase()}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-base" style={{ color: "var(--c-content)" }}>
              {displayName}
            </span>
            <span className="text-xs" style={{ color: "color-mix(in srgb, var(--c-content) 60%, transparent)" }}>
              @{post.author.handle}
            </span>
            <span className="text-xs" style={{ color: "color-mix(in srgb, var(--c-content) 50%, transparent)" }}>
              · {formatTimestamp(post.created_at)}
            </span>
          </div>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: "color-mix(in srgb, var(--c-content) 85%, transparent)" }}>
            {post.text}
          </p>
          {imageUrl && (
            <div className="mt-3 overflow-hidden rounded-xl border border-white/5">
              <Image
                src={imageUrl}
                alt={post.text.slice(0, 40) || "Post media"}
                width={600}
                height={400}
                className="w-full h-auto object-cover"
              />
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
