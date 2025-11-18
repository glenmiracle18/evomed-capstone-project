"use client";

import Link from "next/link";
import { useUser, UserButton } from "@clerk/nextjs";
import { Button } from "~/components/ui/button";
import { CommandPalette } from "~/components/command-palette";
import { ThemeProvider, useTheme } from "~/contexts/theme-context";
import { useEffect, useState } from "react";
import { Moon, Sun, ChevronLeft, ChevronRight, Search, BookOpen } from "lucide-react";

function AppLayoutContent({ children }: { children: React.ReactNode }) {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
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
      {/* Sidebar Navigation - Fixed and Expandable */}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen flex-col border-r border-[#3c4f3d]/10 bg-white py-6 transition-all duration-300 dark:border-[#3c4f3d]/20 dark:bg-[#242924] ${
          sidebarExpanded ? 'w-64' : 'w-16'
        }`}
      >
        {/* Logo */}
        <div className="mb-8 flex items-center gap-3 px-3">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-[#3c4f3d] text-lg font-bold text-white">
            E
          </div>
          {sidebarExpanded && (
            <span className="text-lg font-semibold text-[#3c4f3d] dark:text-white whitespace-nowrap overflow-hidden">
              EvoMed
            </span>
          )}
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-1 flex-col gap-2 px-3">
          <Link href="/app">
            <div className="flex h-10 cursor-pointer items-center gap-3 rounded-lg bg-[#de8246] px-3 text-white transition-colors hover:bg-[#de8246]/90">
              <Search className="h-5 w-5 flex-shrink-0" />
              {sidebarExpanded && (
                <span className="text-sm font-medium whitespace-nowrap overflow-hidden">
                  Variant Search
                </span>
              )}
            </div>
          </Link>

          <Link href="/app/pre-screening">
            <div className="flex h-10 cursor-pointer items-center gap-3 rounded-lg px-3 text-[#3c4f3d]/60 transition-colors hover:bg-[#e9eeea] dark:text-white/60 dark:hover:bg-[#3c4f3d]/20">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 flex-shrink-0"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"></path>
              </svg>
              {sidebarExpanded && (
                <span className="text-sm font-medium whitespace-nowrap overflow-hidden">
                  Pre-Screening
                </span>
              )}
            </div>
          </Link>

          <Link href="/app/docs">
            <div className="flex h-10 cursor-pointer items-center gap-3 rounded-lg px-3 text-[#3c4f3d]/60 transition-colors hover:bg-[#e9eeea] dark:text-white/60 dark:hover:bg-[#3c4f3d]/20">
              <BookOpen className="h-5 w-5 flex-shrink-0" />
              {sidebarExpanded && (
                <span className="text-sm font-medium whitespace-nowrap overflow-hidden">
                  Documentation
                </span>
              )}
            </div>
          </Link>
        </nav>

        {/* Bottom Actions */}
        <div className="mt-auto flex flex-col gap-3 px-3">
          {/* Toggle Sidebar Button */}
          <button
            onClick={() => setSidebarExpanded(!sidebarExpanded)}
            className="flex h-10 items-center justify-center rounded-lg border border-[#3c4f3d]/20 text-[#3c4f3d] transition-colors hover:border-[#de8246] hover:bg-[#de8246]/10 hover:text-[#de8246] dark:border-[#3c4f3d]/30 dark:text-white dark:hover:border-[#de8246] dark:hover:bg-[#de8246]/10"
            aria-label="Toggle sidebar"
          >
            {sidebarExpanded ? (
              <ChevronLeft className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="flex h-10 items-center justify-center rounded-lg border border-[#3c4f3d]/20 text-[#3c4f3d] transition-colors hover:border-[#de8246] hover:bg-[#de8246]/10 hover:text-[#de8246] dark:border-[#3c4f3d]/30 dark:text-white dark:hover:border-[#de8246] dark:hover:bg-[#de8246]/10"
            aria-label="Toggle theme"
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          <div className="flex justify-center">
            <UserButton />
          </div>
        </div>
      </aside>

      {/* Main Content - Add left margin to account for fixed sidebar */}
      <main className={`flex-1 transition-all duration-300 ${
        sidebarExpanded ? 'ml-64' : 'ml-16'
      }`}>
        {children}
      </main>

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
