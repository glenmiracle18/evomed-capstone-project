"use client";

import { useUser, UserButton } from "@clerk/nextjs";
import { Search, HelpCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { ChromosomeMap } from "~/components/chromosome-map";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Tooltip } from "~/components/ui/tooltip";
import {
  type ChromosomeFromSeach,
  type GeneFromSearch,
  type GenomeAssemblyFromSearch,
  getAvailableGenomes,
  getGenomeChromosomes,
  searchGenes,
} from "~/utils/genome-api";

type Mode = "browse" | "search";

export default function HomePage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [genomes, setGenomes] = useState<GenomeAssemblyFromSearch[]>([]);
  const [selectedGenome, setSelectedGenome] = useState<string>("hg38");
  const [chromosomes, setChromosomes] = useState<ChromosomeFromSeach[]>([]);
  const [selectedChromosome, setSelectedChromosome] = useState<string>("chr1");
  const [selectedGene, setSelectedGene] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<GeneFromSearch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("search");
  const [activeExample, setActiveExample] = useState<string | null>(null);

  useEffect(() => {
    const fetchGenomes = async () => {
      try {
        setIsLoading(true);
        const data = await getAvailableGenomes();
        if (data.genomes && data.genomes["Human"]) {
          setGenomes(data.genomes["Human"]);
        }
      } catch (err) {
        setError("Failed to load genome data");
      } finally {
        setIsLoading(false);
      }
    };
    fetchGenomes();
  }, []);

  // Load BRCA1 example by default
  useEffect(() => {
    if (
      genomes.length > 0 &&
      selectedGenome &&
      !searchResults.length &&
      !isLoading
    ) {
      setMode("search");
      setSearchQuery("BRCA1");
      performGeneSearch("BRCA1", selectedGenome);
    }
  }, [genomes, selectedGenome]);

  useEffect(() => {
    const fetchChromosomes = async () => {
      try {
        setIsLoading(true);
        const data = await getGenomeChromosomes(selectedGenome);
        setChromosomes(data.chromosomes);
        console.log(data.chromosomes);
        if (data.chromosomes.length > 0) {
          setSelectedChromosome(data.chromosomes[0]!.name);
        }
      } catch (err) {
        setError("Failed to load chromosome data");
      } finally {
        setIsLoading(false);
      }
    };
    fetchChromosomes();
  }, [selectedGenome]);

  const performGeneSearch = async (
    query: string,
    genome: string,
    filterFn?: (gene: GeneFromSearch) => boolean,
  ) => {
    try {
      setIsLoading(true);
      const data = await searchGenes(query, genome);
      const results = filterFn ? data.results.filter(filterFn) : data.results;

      setSearchResults(results);
    } catch (err) {
      setError("Faield to search genes");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!selectedChromosome || mode !== "browse") return;
    performGeneSearch(
      selectedChromosome,
      selectedGenome,
      (gene: GeneFromSearch) => gene.chrom === selectedChromosome,
    );
  }, [selectedChromosome, selectedGenome, mode]);

  const handleGenomeChange = (value: string) => {
    setSelectedGenome(value);
    setSearchResults([]);
    setSelectedGene(null);
  };

  const switchMode = (newMode: Mode) => {
    if (newMode === mode) return;

    setSearchResults([]);
    setSelectedGene(null);
    setError(null);

    if (newMode === "browse" && selectedChromosome) {
      performGeneSearch(
        selectedChromosome,
        selectedGenome,
        (gene: GeneFromSearch) => gene.chrom === selectedChromosome,
      );
    }

    setMode(newMode);
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    performGeneSearch(searchQuery, selectedGenome);
  };

  const loadBRCA1Example = () => {
    setMode("search");
    setSearchQuery("BRCA1");
    setActiveExample("BRCA1");
    performGeneSearch("BRCA1", selectedGenome);
  };

  const loadHBBExample = () => {
    setMode("search");
    setSearchQuery("HBB");
    setActiveExample("HBB");
    performGeneSearch("HBB", selectedGenome);
  };

  const loadG6PDExample = () => {
    setMode("search");
    setSearchQuery("G6PD");
    setActiveExample("G6PD");
    performGeneSearch("G6PD", selectedGenome);
  };

  const handleGeneSelect = (gene: GeneFromSearch) => {
    // Navigate to dedicated gene page with properly encoded gene symbol
    router.push(
      `/app/gene/${encodeURIComponent(gene.symbol)}?genome=${selectedGenome}`,
    );
  };

  // Handle loading and authentication states
  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#e9eeea]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[#3c4f3d]/30 border-t-[#de8243]"></div>
          <p className="mt-4 text-sm text-[#3c4f3d]/70">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#e9eeea]">
        <div className="text-center">
          <h1 className="mb-4 text-2xl font-light text-[#3c4f3d]">
            Welcome to <span className="font-normal">EvoMed</span>
          </h1>
          <p className="mb-8 text-[#3c4f3d]/70">
            Please sign in to access the application.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      {/* Left Panel - Controls */}
      <div className="w-[420px] border-r border-[#3c4f3d]/10 bg-white p-6 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
        <div className="mb-8">
          <h2 className="mb-1 text-xl font-medium text-[#3c4f3d] dark:text-white">
            Variant Analysis
          </h2>
          <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
            Search and analyze genetic variants
          </p>
        </div>

        {/* Genome Assembly Selector - Compact Pills */}
        <div className="mb-8">
          <div className="mb-3 flex items-center justify-between">
            <label className="text-xs font-medium tracking-wider text-[#3c4f3d]/70 uppercase dark:text-white/70">
              Genome Assembly
            </label>
            <Tooltip content="A genome assembly is a computational representation of a genome sequence. Different assemblies (like hg38, hg19) represent different versions of the human genome reference with varying levels of completeness and accuracy." />
          </div>
          <Select
            value={selectedGenome}
            onValueChange={handleGenomeChange}
            disabled={isLoading}
          >
            <SelectTrigger className="h-10 w-full border border-[#3c4f3d]/20 bg-white dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70">
              <SelectValue placeholder="Select genome assembly" />
            </SelectTrigger>
            <SelectContent>
              {genomes.map((genome) => (
                <SelectItem key={genome.id} value={genome.id}>
                  {genome.id} - {genome.name}
                  {genome.active ? " (active)" : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedGenome && (
            <p className="mt-2 text-xs text-[#3c4f3d]/50 dark:text-white/50">
              {
                genomes.find((genome) => genome.id === selectedGenome)
                  ?.sourceName
              }
            </p>
          )}
        </div>

        {/* Mode Switcher */}
        <div className="mb-6">
          <div className="mb-3 flex items-center justify-between">
            <label className="text-xs font-medium tracking-wider text-[#3c4f3d]/70 uppercase dark:text-white/70">
              Search Method
            </label>
            <Tooltip content="Search for specific genes by name or symbol, or browse genes by chromosome. Use the search function to find genes like BRCA1, or browse chromosomes to see all genes in a specific region." />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => switchMode("search")}
              className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors ${
                mode === "search"
                  ? "border-[#de8246] bg-[#de8246] text-white"
                  : "border-[#3c4f3d]/20 bg-white text-[#3c4f3d]/70 hover:border-[#3c4f3d]/30 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
              }`}
            >
              Search Genes
            </button>
            <button
              onClick={() => switchMode("browse")}
              className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors ${
                mode === "browse"
                  ? "border-[#de8246] bg-[#de8246] text-white"
                  : "border-[#3c4f3d]/20 bg-white text-[#3c4f3d]/70 hover:border-[#3c4f3d]/30 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
              }`}
            >
              Browse Chromosomes
            </button>
          </div>
        </div>

        {/* Search Mode */}
        {mode === "search" && (
          <div className="mb-6">
            <div className="mb-3">
              <label className="text-xs font-medium tracking-wider text-[#3c4f3d]/70 uppercase dark:text-white/70">
                Gene Search
              </label>
            </div>
            <form onSubmit={handleSearch}>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Enter gene symbol or name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-11 border-[#3c4f3d]/20 pr-11 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
                />
                <Button
                  type="submit"
                  className="absolute top-0 right-0 h-11 cursor-pointer rounded-l-none bg-[#3c4f3d] text-white hover:bg-[#3c4f3d]/90"
                  size="icon"
                  disabled={isLoading || !searchQuery.trim()}
                >
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </form>

            {/* Quick Examples */}
            <div className="mt-4 space-y-2">
              <p className="text-xs text-[#3c4f3d]/50 dark:text-white/50">
                Quick examples:
              </p>
              <div className="flex flex-col gap-2">
                <button
                  onClick={loadBRCA1Example}
                  className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                    activeExample === "BRCA1"
                      ? "border-[#de8246] bg-[#de8246]/5 text-[#de8246]"
                      : "border-[#3c4f3d]/10 bg-white text-[#3c4f3d]/70 hover:border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
                  }`}
                >
                  BRCA1
                </button>
                <button
                  onClick={loadHBBExample}
                  className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                    activeExample === "HBB"
                      ? "border-[#de8246] bg-[#de8246]/5 text-[#de8246]"
                      : "border-[#3c4f3d]/10 bg-white text-[#3c4f3d]/70 hover:border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
                  }`}
                >
                  HBB <span className="text-xs opacity-60">(Sickle Cell)</span>
                </button>
                <button
                  onClick={loadG6PDExample}
                  className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                    activeExample === "G6PD"
                      ? "border-[#de8246] bg-[#de8246]/5 text-[#de8246]"
                      : "border-[#3c4f3d]/10 bg-white text-[#3c4f3d]/70 hover:border-[#3c4f3d]/20 dark:border-[#3c4f3d]/30 dark:bg-[#1a1f1a] dark:text-white/70"
                  }`}
                >
                  G6PD <span className="text-xs opacity-60">(Deficiency)</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Browse Mode */}
        {mode === "browse" && (
          <div className="mb-6">
            <ChromosomeMap
              chromosomes={chromosomes}
              selectedChromosome={selectedChromosome}
              onSelectChromosome={setSelectedChromosome}
            />
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Right Panel - Results */}
      <div className="flex-1 overflow-y-auto bg-[#e9eeea] p-6 dark:bg-[#1a1f1a]">
        {isLoading && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[#3c4f3d]/30 border-t-[#de8246]"></div>
              <p className="mt-4 text-sm text-[#3c4f3d]/70 dark:text-white/70">
                Loading genes...
              </p>
            </div>
          </div>
        )}

        {!isLoading && !error && searchResults.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white dark:bg-[#242924]">
                <Search className="h-8 w-8 text-[#3c4f3d]/30 dark:text-white/30" />
              </div>
              <h3 className="mb-2 text-lg font-medium text-[#3c4f3d] dark:text-white">
                {mode === "search" ? "Search for genes" : "Select a chromosome"}
              </h3>
              <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
                {mode === "search"
                  ? "Enter a gene symbol or name to get started"
                  : "Choose a chromosome to browse available genes"}
              </p>
            </div>
          </div>
        )}

        {searchResults.length > 0 && !isLoading && (
          <div>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-[#3c4f3d] dark:text-white">
                  {mode === "search"
                    ? "Search Results"
                    : `Chromosome ${selectedChromosome}`}
                </h3>
                <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
                  {searchResults.length}{" "}
                  {searchResults.length === 1 ? "gene" : "genes"} found
                </p>
              </div>
              <Tooltip
                content={
                  mode === "search"
                    ? "Click on any gene to view detailed information including gene sequence, variants, and analysis tools."
                    : `Click on any gene to explore detailed information. Results show all genes on chromosome ${selectedChromosome}.`
                }
              />
            </div>

            <div className="space-y-2">
              {searchResults.map((gene, index) => (
                <div
                  key={`${gene.symbol}-${index}`}
                  onClick={() => handleGeneSelect(gene)}
                  className="cursor-pointer rounded-lg border border-[#3c4f3d]/10 bg-white p-4 transition-all hover:border-[#de8246] hover:bg-white dark:border-[#3c4f3d]/20 dark:bg-[#242924] dark:hover:border-[#de8246]"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="mb-1 flex items-center gap-2">
                        <h4 className="font-medium text-[#3c4f3d] dark:text-white">
                          {gene.symbol}
                        </h4>
                        <span className="rounded-full bg-[#e9eeea] px-2 py-0.5 text-xs font-medium text-[#3c4f3d]/70 dark:bg-[#1a1f1a] dark:text-white/70">
                          {gene.chrom}
                        </span>
                      </div>
                      <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
                        {gene.name}
                      </p>
                    </div>
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
                      className="text-[#3c4f3d]/30 dark:text-white/30"
                    >
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
