import Link from "next/link";
import { Megaphone, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { ModeToggle } from "../mode-toggle";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-border/50 bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
          <Megaphone className="h-6 w-6 text-primary" />
          OUR Voice
        </Link>
        <div className="hidden flex-1 items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-3 py-1.5 sm:flex">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input type="search" placeholder="Buscar posts ou pessoas" className="h-7 border-none bg-transparent text-sm shadow-none focus-visible:ring-0" />
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" className="hidden sm:inline-flex">
            Entrar
          </Button>
          <Button>Registrar</Button>
          <ModeToggle />
        </div>
      </div>
    </header>
  );
}
