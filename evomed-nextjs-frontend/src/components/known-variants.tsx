"use client";

import {
  analyzeVariantWithAPI,
  type ClinvarVariant,
  type GeneFromSearch,
} from "~/utils/genome-api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { Viaoda_Libre } from "next/font/google";
import {
  BarChart2,
  ExternalLink,
  RefreshCw,
  Search,
  Shield,
  Zap,
  HelpCircle,
} from "lucide-react";
import { Tooltip } from "./ui/tooltip";
import { getClassificationColorClasses } from "~/utils/coloring-utils";

export default function KnownVariants({
  refreshVariants,
  showComparison,
  updateClinvarVariant,
  clinvarVariants,
  isLoadingClinvar,
  clinvarError,
  genomeId,
  gene,
  useAfricanAdjustment = true,
}: {
  refreshVariants: () => void;
  showComparison: (variant: ClinvarVariant) => void;
  updateClinvarVariant: (id: string, newVariant: ClinvarVariant) => void;
  clinvarVariants: ClinvarVariant[];
  isLoadingClinvar: boolean;
  clinvarError: string | null;
  genomeId: string;
  gene: GeneFromSearch;
  useAfricanAdjustment?: boolean;
}) {
  const analyzeVariant = async (variant: ClinvarVariant) => {
    let variantDetails = null;
    const position = variant.location
      ? parseInt(variant.location.replaceAll(",", ""))
      : null;

    const refAltMatch = variant.title.match(/(\w)>(\w)/);

    if (refAltMatch && refAltMatch.length === 3) {
      variantDetails = {
        position,
        reference: refAltMatch[1],
        alternative: refAltMatch[2],
      };
    }

    if (
      !variantDetails ||
      !variantDetails.position ||
      !variantDetails.reference ||
      !variantDetails.alternative
    ) {
      return;
    }

    updateClinvarVariant(variant.clinvar_id, {
      ...variant,
      isAnalyzing: true,
    });

    try {
      const data = await analyzeVariantWithAPI({
        position: variantDetails.position,
        alternative: variantDetails.alternative,
        genomeId: genomeId,
        chromosome: gene.chrom,
        useAfricanAdjustment,
      });

      const updatedVariant: ClinvarVariant = {
        ...variant,
        isAnalyzing: false,
        evo2Result: data,
      };

      updateClinvarVariant(variant.clinvar_id, updatedVariant);

      showComparison(updatedVariant);
    } catch (error) {
      updateClinvarVariant(variant.clinvar_id, {
        ...variant,
        isAnalyzing: false,
        evo2Error: error instanceof Error ? error.message : "Analysis failed",
      });
    }
  };
  return (
    <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-5 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-base font-medium text-[#3c4f3d] dark:text-white">
            Known Variants from ClinVar
          </h3>
          <Tooltip content="ClinVar is a public database containing information about genetic variants and their clinical significance. These are known variants in this gene with classifications like pathogenic, benign, or uncertain significance from clinical studies." />
        </div>
        <button
          onClick={refreshVariants}
          disabled={isLoadingClinvar}
          className="flex items-center gap-1.5 rounded-lg border border-[#3c4f3d]/20 bg-white px-3 py-1.5 text-sm text-[#3c4f3d] transition-colors hover:bg-[#e9eeea]/50 disabled:opacity-50"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>
      {clinvarError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {clinvarError}
        </div>
      )}

      {isLoadingClinvar ? (
        <div className="flex justify-center py-8">
          <div className="text-center">
            <div className="mx-auto h-6 w-6 animate-spin rounded-full border-2 border-[#3c4f3d]/30 border-t-[#de8246]"></div>
            <p className="mt-3 text-sm text-[#3c4f3d]/70 dark:text-white/70">
              Loading variants...
            </p>
          </div>
        </div>
      ) : clinvarVariants.length > 0 ? (
        <div className="max-h-[500px] space-y-2 overflow-y-auto">
          {clinvarVariants.map((variant) => (
            <div
              key={variant.clinvar_id}
              className="rounded-lg border border-[#3c4f3d]/10 bg-[#e9eeea]/20 dark:bg-[#1a1f1a]/30 p-4 transition-colors hover:border-[#3c4f3d]/20"
            >
              <div className="mb-3 flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[#3c4f3d] dark:text-white">
                    {variant.title}
                  </h4>
                  <div className="mt-1 flex items-center gap-2 text-xs text-[#3c4f3d]/60 dark:text-white/60">
                    <span>Location: {variant.location}</span>
                    <span>•</span>
                    <button
                      onClick={() =>
                        window.open(
                          `https://www.ncbi.nlm.nih.gov/clinvar/variation/${variant.clinvar_id}`,
                          "_blank",
                        )
                      }
                      className="flex items-center gap-1 text-[#de8246] hover:text-[#de8246]/80"
                    >
                      View in ClinVar
                      <ExternalLink className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div>
                  <div className="mb-1 text-xs font-medium tracking-wider text-[#3c4f3d]/70 dark:text-white/70 uppercase">
                    Type
                  </div>
                  <div className="text-sm text-[#3c4f3d] dark:text-white">
                    {variant.variation_type}
                  </div>
                </div>

                <div>
                  <div className="mb-1 text-xs font-medium tracking-wider text-[#3c4f3d]/70 dark:text-white/70 uppercase">
                    Clinical Significance
                  </div>
                  <div
                    className={`inline-block rounded-md px-2 py-1 text-xs font-medium ${getClassificationColorClasses(variant.classification)}`}
                  >
                    {variant.classification || "Unknown"}
                  </div>
                  {variant.evo2Result && (
                    <div className="mt-1">
                      <div
                        className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium ${getClassificationColorClasses(variant.evo2Result.prediction)}`}
                      >
                        <Shield className="h-3 w-3" />
                        Evo2: {variant.evo2Result.prediction}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-end justify-end">
                  {variant.variation_type
                    .toLowerCase()
                    .includes("single nucleotide") ? (
                    !variant.evo2Result ? (
                      <button
                        disabled={variant.isAnalyzing}
                        onClick={() => analyzeVariant(variant)}
                        className="flex h-9 items-center gap-1.5 rounded-lg border border-[#de8246]/30 bg-[#de8246]/10 px-3 text-sm font-medium text-[#de8246] transition-colors hover:bg-[#de8246]/20 disabled:opacity-50"
                      >
                        {variant.isAnalyzing ? (
                          <>
                            <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-[#de8246]/30 border-t-[#de8246]"></span>
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Zap className="h-3.5 w-3.5" />
                            Analyze with Evo2
                          </>
                        )}
                      </button>
                    ) : (
                      <button
                        onClick={() => showComparison(variant)}
                        className="flex h-9 items-center gap-1.5 rounded-lg border border-green-200 bg-green-50 px-3 text-sm font-medium text-green-700 transition-colors hover:bg-green-100"
                      >
                        <BarChart2 className="h-3.5 w-3.5" />
                        Compare Results
                      </button>
                    )
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex h-48 flex-col items-center justify-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#e9eeea]">
            <Search className="h-6 w-6 text-[#3c4f3d]/30" />
          </div>
          <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
            No ClinVar variants found for this gene
          </p>
        </div>
      )}
    </div>
  );
}
