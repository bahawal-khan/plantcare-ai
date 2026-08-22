"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { siteConfig } from "@/lib/site-config";
import { LinkButton } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Container } from "@/components/ui/Container";
import { MenuIcon, XIcon } from "@/components/ui/icons";

function LeafMark() {
  return (
    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 shadow-sm shadow-brand-900/20">
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden="true">
        <path d="M4 20c8 0 14-6 14-16-9 0-14 6-14 16Z" fill="white" />
        <path d="M4 20c3-6 7-10 13-13" stroke="#16a34a" strokeWidth="1.4" strokeLinecap="round" />
      </svg>
    </span>
  );
}

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));

  return (
    <header className="sticky top-0 z-40 border-b border-border-default bg-surface/80 backdrop-blur-md">
      <Container className="flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 font-semibold text-text-strong">
          <LeafMark />
          <span className="text-lg tracking-tight">{siteConfig.name}</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {siteConfig.nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive(item.href) ? "page" : undefined}
              className={`rounded-full px-3.5 py-2 text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? "bg-brand-500/10 text-brand-700 dark:text-brand-400"
                  : "text-text-body hover:text-text-strong"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <LinkButton href="/diagnose" variant="primary" size="sm">
            Diagnose Now
          </LinkButton>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation menu"
            aria-expanded={open}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border-default text-text-strong"
          >
            {open ? <XIcon className="h-5 w-5" /> : <MenuIcon className="h-5 w-5" />}
          </button>
        </div>
      </Container>

      {open && (
        <div className="border-t border-border-default bg-surface px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {siteConfig.nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                aria-current={isActive(item.href) ? "page" : undefined}
                className={`rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive(item.href) ? "bg-brand-500/10 text-brand-700 dark:text-brand-400" : "text-text-body"
                }`}
              >
                {item.label}
              </Link>
            ))}
            <LinkButton
              href="/diagnose"
              variant="primary"
              className="mt-2 justify-center"
              onClick={() => setOpen(false)}
            >
              Diagnose Now
            </LinkButton>
          </nav>
        </div>
      )}
    </header>
  );
}
