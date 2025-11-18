"use client";

import Link from "next/link";
import { useUser, UserButton } from "@clerk/nextjs";
import { Button } from "~/components/ui/button";
import { CommandPalette } from "~/components/command-palette";
import { ThemeProvider, useTheme } from "~/contexts/theme-context";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

function AppLayoutContent({ children }: { children: React.ReactNode }) {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="flex min-h-screen bg-[#e9eeea] dark:bg-[#1a1f1a]">
      {/* Sidebar Navigation */}
      <aside className="flex w-16 flex-col items-center border-r border-[#3c4f3d]/10 bg-white py-6 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
        <div className="mb-8 flex h-10 w-10 items-center justify-center rounded-lg bg-[#3c4f3d] text-lg font-bold text-white">
          E
        </div>

        <nav className="flex flex-1 flex-col gap-4">
          <Link href="/app">
            <div className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg bg-[#de8246] text-white transition-colors hover:bg-[#de8246]/90">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
            </div>
          </Link>

          <Link href="/app/pre-screening">
            <div className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg text-[#3c4f3d]/60 transition-colors hover:bg-[#e9eeea] dark:text-white/60 dark:hover:bg-[#3c4f3d]/20">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"></path>
              </svg>
            </div>
          </Link>

          <Link href="/app/docs">
            <div className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg text-[#3c4f3d]/60 transition-colors hover:bg-[#e9eeea] dark:text-white/60 dark:hover:bg-[#3c4f3d]/20">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
            </div>
          </Link>
        </nav>

        <div className="mt-auto flex flex-col gap-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-[#3c4f3d]/60 transition-colors hover:bg-[#e9eeea] dark:text-white/60 dark:hover:bg-[#3c4f3d]/20"
            aria-label="Toggle theme"
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          <UserButton />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />
    </div>
  );
}

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <AppLayoutContent>{children}</AppLayoutContent>
        </ThemeProvider>
      </body>
    </html>
  );
}
