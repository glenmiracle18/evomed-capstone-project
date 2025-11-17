"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useUser, UserButton } from "@clerk/nextjs";
import GeneViewer from "~/components/gene-viewer";
import { searchGenes, type GeneFromSearch } from "~/utils/genome-api";

export default function GenePage() {
  const { user, isLoaded } = useUser();
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [gene, setGene] = useState<GeneFromSearch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const geneSymbol = decodeURIComponent(params.symbol as string);
  const genomeId = searchParams.get("genome") || "hg38";

  useEffect(() => {
    const fetchGene = async () => {
      if (!geneSymbol) return;

      try {
        setIsLoading(true);
        const data = await searchGenes(geneSymbol, genomeId);
        const foundGene = data.results.find(
          (g) => g.symbol.toLowerCase() === geneSymbol.toLowerCase(),
        );

        if (foundGene) {
          setGene(foundGene);
        } else {
          setError(`Gene "${geneSymbol}" not found`);
        }
      } catch (err) {
        setError("Failed to load gene data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchGene();
  }, [geneSymbol, genomeId]);

  const handleClose = () => {
    // Navigate back to the main app page, preserving genome parameter if it exists
    const backUrl = genomeId !== "hg38" ? `/app?genome=${genomeId}` : "/app";
    router.push(backUrl);
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

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#e9eeea]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[#3c4f3d]/30 border-t-[#de8243]"></div>
          <p className="mt-4 text-sm text-[#3c4f3d]/70">Loading gene data...</p>
        </div>
      </div>
    );
  }

  if (error || !gene) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#e9eeea]">
        <div className="text-center">
          <h1 className="mb-4 text-2xl font-light text-[#3c4f3d]">
            Gene Not Found
          </h1>
          <p className="mb-8 text-[#3c4f3d]/70">{error}</p>
          <button
            onClick={handleClose}
            className="rounded bg-[#3c4f3d] px-4 py-2 text-white hover:bg-[#3c4f3d]/90"
          >
            Back to Search
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-y-auto bg-[#e9eeea] dark:bg-[#1a1f1a]">
      <GeneViewer gene={gene} genomeId={genomeId} onClose={handleClose} />
    </div>
  );
}
