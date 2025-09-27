import { AlertTriangle, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export function ModerationBanner() {
  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Users className="h-6 w-6 text-primary" />
          <div>
            <p className="font-semibold">Moderação pela comunidade</p>
            <p className="text-sm text-muted-foreground">
              Vote para ocultar conteúdos nocivos ou remova coletivamente quando o limiar democrático for atingido.
            </p>
          </div>
        </div>
        <Badge variant="outline" className="gap-2 text-sm">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          Carregando estatísticas...
        </Badge>
      </CardContent>
    </Card>
  );
}
