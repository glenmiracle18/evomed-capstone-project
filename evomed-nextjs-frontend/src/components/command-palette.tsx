"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, Clock, Dna, BookOpen, Command } from "lucide-react";
import { searchGenes, type GeneFromSearch } from "~/utils/genome-api";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  genomeId?: string;
}

export function CommandPalette({
  isOpen,
  onClose,
  genomeId = "hg38",
}: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GeneFromSearch[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Load recent searches from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("recentSearches");
    if (stored) {
      setRecentSearches(JSON.parse(stored));
    }
  }, []);

  // Search functionality
  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }

    const searchTimer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const data = await searchGenes(query, genomeId);
        setResults(data.results.slice(0, 8)); // Limit to 8 results
      } catch (error) {
        console.error("Search error:", error);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(searchTimer);
  }, [query, genomeId]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (results[selectedIndex]) {
            handleSelectGene(results[selectedIndex]);
          }
          break;
        case "Escape":
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose]);

  const handleSelectGene = (gene: GeneFromSearch) => {
    // Save to recent searches
    const updated = [
      gene.symbol,
      ...recentSearches.filter((s) => s !== gene.symbol),
    ].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem("recentSearches", JSON.stringify(updated));

    // Navigate to gene
    router.push(
      `/app/gene/${encodeURIComponent(gene.symbol)}?genome=${genomeId}`,
    );
    onClose();
  };

  const handleRecentSearch = (geneSymbol: string) => {
    setQuery(geneSymbol);
  };

  const quickActions = [
    {
      icon: BookOpen,
      label: "Documentation",
      action: () => router.push("/app/docs"),
    },
    {
      icon: Dna,
      label: "Browse Chromosomes",
      action: () => router.push("/app"),
    },
  ];

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Command Palette */}
      <div className="fixed top-[20%] left-1/2 z-50 w-full max-w-2xl -translate-x-1/2 px-4">
        <div className="overflow-hidden rounded-xl border border-[#3c4f3d]/20 bg-white shadow-2xl dark:bg-[#242924]">
          {/* Search Input */}
          <div className="flex items-center gap-3 border-b border-[#3c4f3d]/10 p-4">
            <Search className="h-5 w-5 text-[#3c4f3d]/40 dark:text-white/40" />
            <input
              type="text"
              placeholder="Search genes..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent text-[#3c4f3d] outline-none placeholder:text-[#3c4f3d]/40 dark:text-white/40"
              autoFocus
            />
            <div className="flex items-center gap-1 text-xs text-[#3c4f3d]/40 dark:text-white/40">
              <kbd className="rounded bg-[#e9eeea] dark:bg-[#3c4f3d]/20 px-1.5 py-0.5 font-mono">
                ESC
              </kbd>
            </div>
          </div>

          {/* Results */}
          <div className="max-h-[400px] overflow-y-auto">
            {query.trim().length === 0 && (
              <div className="p-4">
                {/* Recent Searches */}
                {recentSearches.length > 0 && (
                  <div className="mb-4">
                    <div className="mb-2 flex items-center gap-2 text-xs font-medium text-[#3c4f3d]/70">
                      <Clock className="h-3.5 w-3.5" />
                      Recent Searches
                    </div>
                    <div className="space-y-1">
                      {recentSearches.map((gene, index) => (
                        <button
                          key={index}
                          onClick={() => handleRecentSearch(gene)}
                          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors hover:bg-[#e9eeea]/50 dark:bg-[#1a1f1a]/50"
                        >
                          <Dna className="h-4 w-4 text-[#de8246]" />
                          <span className="text-sm text-[#3c4f3d] dark:text-white">{gene}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Actions */}
                <div>
                  <div className="mb-2 text-xs font-medium text-[#3c4f3d]/70">
                    Quick Actions
                  </div>
                  <div className="space-y-1">
                    {quickActions.map((action, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          action.action();
                          onClose();
                        }}
                        className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors hover:bg-[#e9eeea]/50 dark:bg-[#1a1f1a]/50"
                      >
                        <action.icon className="h-4 w-4 text-[#de8246]" />
                        <span className="text-sm text-[#3c4f3d] dark:text-white">
                          {action.label}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {isSearching && (
              <div className="flex items-center justify-center p-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#3c4f3d]/30 border-t-[#de8246]"></div>
              </div>
            )}

            {!isSearching &&
              query.trim().length > 0 &&
              results.length === 0 && (
                <div className="p-8 text-center">
                  <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">No genes found</p>
                </div>
              )}

            {!isSearching && results.length > 0 && (
              <div className="p-2">
                {results.map((gene, index) => (
                  <button
                    key={`${gene.symbol}-${index}`}
                    onClick={() => handleSelectGene(gene)}
                    className={`flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left transition-colors ${
                      index === selectedIndex
                        ? "bg-[#de8246]/10"
                        : "hover:bg-[#e9eeea]/50 dark:bg-[#1a1f1a]/50"
                    }`}
                  >
                    <Dna
                      className={`mt-0.5 h-4 w-4 ${index === selectedIndex ? "text-[#de8246]" : "text-[#3c4f3d]/40 dark:text-white/40"}`}
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-[#3c4f3d] dark:text-white">
                          {gene.symbol}
                        </span>
                        <span className="rounded-full bg-[#e9eeea] dark:bg-[#3c4f3d]/20 px-2 py-0.5 text-xs text-[#3c4f3d]/70">
                          {gene.chrom}
                        </span>
                      </div>
                      <p className="mt-0.5 truncate text-sm text-[#3c4f3d]/60 dark:text-white/60">
                        {gene.name}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-[#3c4f3d]/10 bg-[#e9eeea]/30 dark:bg-[#1a1f1a]/50 px-4 py-2">
            <div className="flex items-center gap-3 text-xs text-[#3c4f3d]/60 dark:text-white/60">
              <span className="flex items-center gap-1">
                <kbd className="rounded bg-white px-1.5 py-0.5 font-mono">
                  ↑↓
                </kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="rounded bg-white px-1.5 py-0.5 font-mono">
                  ↵
                </kbd>
                Select
              </span>
            </div>
            <div className="flex items-center gap-1 text-xs text-[#3c4f3d]/40 dark:text-white/40">
              <Command className="h-3 w-3" />
              <span>K</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
