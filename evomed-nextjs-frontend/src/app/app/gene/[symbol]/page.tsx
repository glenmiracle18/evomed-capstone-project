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
  const variantPosition = searchParams.get("position");
  const variantAlt = searchParams.get("alt");
  const chromosome = searchParams.get("chromosome");

  useEffect(() => {
    const fetchGene = async () => {
      if (!geneSymbol) return;

      let retries = 0;
      const maxRetries = 3;

      while (retries < maxRetries) {
        try {
          setIsLoading(true);
          const data = await searchGenes(geneSymbol, genomeId);

          // Try to find exact match first
          let foundGene = data.results.find(
            (g) => g.symbol.toLowerCase() === geneSymbol.toLowerCase(),
          );

          // If found but missing gene_id, try to get it from other results
          if (foundGene && !foundGene.gene_id) {
            console.warn(`[GenePage] Found ${geneSymbol} but missing gene_id, checking other results`);
            // Sometimes the exact match doesn't have gene_id but another result does
            const alternativeWithId = data.results.find(
              (g) => g.symbol.toLowerCase() === geneSymbol.toLowerCase() && g.gene_id
            );
            if (alternativeWithId) {
              foundGene = alternativeWithId;
              console.log(`[GenePage] Found alternative with gene_id: ${alternativeWithId.gene_id}`);
            }
          }

          // Common cancer genes with their chromosome locations and NCBI gene IDs
          const commonGenes: Record<string, { chrom: string; description: string; gene_id: string }> = {
            'BRCA1': { chrom: 'chr17', description: 'BRCA1 DNA repair associated', gene_id: '672' },
            'BRCA2': { chrom: 'chr13', description: 'BRCA2 DNA repair associated', gene_id: '675' },
            'TP53': { chrom: 'chr17', description: 'Tumor protein p53', gene_id: '7157' },
            'PALB2': { chrom: 'chr16', description: 'Partner and localizer of BRCA2', gene_id: '79728' },
            'ATM': { chrom: 'chr11', description: 'ATM serine/threonine kinase', gene_id: '472' },
            'CHEK2': { chrom: 'chr22', description: 'Checkpoint kinase 2', gene_id: '11200' },
            'CDH1': { chrom: 'chr16', description: 'Cadherin 1', gene_id: '999' },
            'PTEN': { chrom: 'chr10', description: 'Phosphatase and tensin homolog', gene_id: '5728' },
            'STK11': { chrom: 'chr19', description: 'Serine/threonine kinase 11', gene_id: '6794' },
            'RAD51C': { chrom: 'chr17', description: 'RAD51 paralog C', gene_id: '5889' },
            'RAD51D': { chrom: 'chr17', description: 'RAD51 paralog D', gene_id: '5892' },
            'BARD1': { chrom: 'chr2', description: 'BRCA1 associated RING domain 1', gene_id: '580' },
            'BRIP1': { chrom: 'chr17', description: 'BRCA1 interacting protein C-terminal helicase 1', gene_id: '83990' },
          };

          // If found with gene_id, use API result
          if (foundGene && foundGene.gene_id) {
            console.log(`[GenePage] Successfully loaded ${geneSymbol} with gene_id: ${foundGene.gene_id}`);
            setGene(foundGene);
            return;
          }

          // If found but missing gene_id, use fallback gene_id if available
          if (foundGene && !foundGene.gene_id) {
            const fallbackInfo = commonGenes[geneSymbol.toUpperCase()];
            if (fallbackInfo) {
              console.log(`[GenePage] Using fallback gene_id for ${geneSymbol}: ${fallbackInfo.gene_id}`);
              setGene({
                ...foundGene,
                gene_id: fallbackInfo.gene_id,
              });
              return;
            }
          }

          // If not found in API results at all, use complete fallback
          if (!foundGene && chromosome) {
            const geneInfo = commonGenes[geneSymbol.toUpperCase()];
            if (geneInfo) {
              console.log(`[GenePage] Using complete fallback for ${geneSymbol}`);
              setGene({
                symbol: geneSymbol.toUpperCase(),
                name: geneInfo.description,
                chrom: geneInfo.chrom,
                description: geneInfo.description,
                gene_id: geneInfo.gene_id,
              });
              return;
            }
          }

          // If still not found after last retry, show error
          if (retries === maxRetries - 1) {
            setError(`Gene "${geneSymbol}" not found`);
          }

        } catch (err) {
          if (retries === maxRetries - 1) {
            setError("Failed to load gene data");
          }
        } finally {
          setIsLoading(false);
        }

        retries++;
        // Wait before retry (exponential backoff: 500ms, 1s, 2s)
        if (retries < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 500 * Math.pow(2, retries - 1)));
        }
      }
    };

    fetchGene();
  }, [geneSymbol, genomeId, chromosome]);

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
      <GeneViewer
        gene={gene}
        genomeId={genomeId}
        onClose={handleClose}
        initialVariantPosition={variantPosition}
        initialVariantAlt={variantAlt}
      />
    </div>
  );
}
