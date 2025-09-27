"use client";

import { useState } from "react";
import { ImageIcon, Loader2, Send } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

export function PostComposer() {
  const [value, setValue] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!value.trim()) return;
    try {
      setSubmitting(true);
      await new Promise((resolve) => setTimeout(resolve, 600));
      setValue("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="border-muted-foreground/10">
      <CardContent className="flex gap-4 p-4">
        <Avatar>
          <AvatarFallback>OV</AvatarFallback>
        </Avatar>
        <div className="flex w-full flex-col gap-3">
          <Textarea
            value={value}
            onChange={(event) => setValue(event.target.value)}
            placeholder="Compartilhe algo com a comunidade..."
            maxLength={500}
          />
          <div className="flex items-center gap-3">
            <Button type="button" variant="ghost" size="sm" className="gap-2">
              <ImageIcon className="h-4 w-4" />
              Imagem
            </Button>
            <div className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
              <span>{value.length}/500</span>
              <Button type="button" size="sm" onClick={handleSubmit} disabled={submitting || !value.trim()}>
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                <span className="ml-2">Postar</span>
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
