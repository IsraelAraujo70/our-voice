import {
  Archive,
  Bookmark,
  Heart,
  MessageCircle,
  Repeat2,
  ShieldAlert,
} from "lucide-react";
import Image from "next/image";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export interface PostCardProps {
  author: {
    handle: string;
    displayName: string;
    avatarUrl?: string;
  };
  createdAt: string;
  text: string;
  imageUrl?: string;
  counts: {
    likes: number;
    replies: number;
    reposts: number;
    votes: number;
  };
  archived?: boolean;
}

export function PostCard({ author, createdAt, text, imageUrl, counts, archived }: PostCardProps) {
  return (
    <Card className="border-muted-foreground/10">
      <CardContent className="space-y-3 p-4">
        <header className="flex items-start justify-between gap-3">
          <div className="flex gap-3">
            <Avatar>
              {author.avatarUrl ? <AvatarImage src={author.avatarUrl} alt={author.displayName} /> : null}
              <AvatarFallback>{author.displayName.slice(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-semibold">{author.displayName}</span>
                <span className="text-muted-foreground">@{author.handle}</span>
                <Separator orientation="vertical" className="h-4" />
                <span className="text-muted-foreground">{createdAt}</span>
              </div>
              {archived ? <Badge variant="outline">Arquivado pela comunidade</Badge> : null}
            </div>
          </div>
          <Button variant="ghost" size="sm" className="text-muted-foreground">
            <Archive className="mr-2 h-4 w-4" />
            Histórico
          </Button>
        </header>
        <p className="whitespace-pre-line text-sm leading-6 text-foreground">{text}</p>
        {imageUrl ? (
          <div className="overflow-hidden rounded-lg border border-border/50">
            <Image src={imageUrl} alt="Imagem do post" width={600} height={400} className="h-auto w-full" />
          </div>
        ) : null}
        <footer className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <ActionIcon icon={Heart} label="Curtir" count={counts.likes} />
          <ActionIcon icon={MessageCircle} label="Debater" count={counts.replies} />
          <ActionIcon icon={Repeat2} label="Repostar" count={counts.reposts} />
          <ActionIcon icon={Bookmark} label="Salvar" count={0} />
          <ActionIcon icon={ShieldAlert} label="Votar remover" count={counts.votes} className="text-destructive" />
        </footer>
      </CardContent>
    </Card>
  );
}

interface ActionIconProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  count: number;
  className?: string;
}

function ActionIcon({ icon: Icon, label, count, className }: ActionIconProps) {
  return (
    <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground" aria-label={label}>
      <Icon className={`h-4 w-4 ${className ?? ""}`} />
      <span>{label}</span>
      <span className="font-medium text-foreground">{count}</span>
    </Button>
  );
}
