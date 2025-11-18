"use client";

import {
  fetchGeneDetails,
  fetchGeneSequence as apiFetchGeneSequence,
  fetchClinvarVariants as apiFetchClinvarVariants,
  type GeneBounds,
  type GeneDetailsFromSearch,
  type GeneFromSearch,
  type ClinvarVariant,
} from "~/utils/genome-api";
import { Button } from "./ui/button";
import { ArrowLeft } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { GeneInformation } from "./gene-information";
import { GeneSequence } from "./gene-sequence";
import KnownVariants from "./known-variants";
import { VariantComparisonModal } from "./variant-comparison-modal";
import VariantAnalysis, {
  type VariantAnalysisHandle,
} from "./variant-analysis";
import { DNAHelix3D } from "./dna-helix-3d";

export default function GeneViewer({
  gene,
  genomeId,
  onClose,
  initialVariantPosition,
  initialVariantAlt,
}: {
  gene: GeneFromSearch;
  genomeId: string;
  onClose: () => void;
  initialVariantPosition?: string | null;
  initialVariantAlt?: string | null;
}) {
  const [geneSequence, setGeneSequence] = useState("");
  const [geneDetail, setGeneDetail] = useState<GeneDetailsFromSearch | null>(
    null,
  );
  const [geneBounds, setGeneBounds] = useState<GeneBounds | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [startPosition, setStartPosition] = useState<string>("");
  const [endPosition, setEndPosition] = useState<string>("");
  const [isLoadingSequence, setIsLoadingSequence] = useState(false);

  const [clinvarVariants, setClinvarVariants] = useState<ClinvarVariant[]>([]);
  const [isLoadingClinvar, setIsLoadingClinvar] = useState(false);
  const [clinvarError, setClinvarError] = useState<string | null>(null);

  const [actualRange, setActualRange] = useState<{
    start: number;
    end: number;
  } | null>(null);

  const [comparisonVariant, setComparisonVariant] =
    useState<ClinvarVariant | null>(null);

  const [activeSequencePosition, setActiveSequencePosition] = useState<
    number | null
  >(initialVariantPosition ? parseInt(initialVariantPosition) : null);
  const [activeReferenceNucleotide, setActiveReferenceNucleotide] = useState<
    string | null
  >(null);
  const [prefilledAlt, setPrefilledAlt] = useState<string | null>(
    initialVariantAlt || null
  );

  // African Population Adjustment state
  const [useAfricanAdjustment, setUseAfricanAdjustment] = useState(true);

  const variantAnalysisRef = useRef<VariantAnalysisHandle>(null);

  const updateClinvarVariant = (
    clinvar_id: string,
    updateVariant: ClinvarVariant,
  ) => {
    setClinvarVariants((currentVariants) =>
      currentVariants.map((v) =>
        v.clinvar_id == clinvar_id ? updateVariant : v,
      ),
    );
  };

  const fetchGeneSequence = useCallback(
    async (start: number, end: number) => {
      try {
        setIsLoadingSequence(true);
        setError(null);

        const {
          sequence,
          actualRange: fetchedRange,
          error: apiError,
        } = await apiFetchGeneSequence(gene.chrom, start, end, genomeId);

        setGeneSequence(sequence);
        setActualRange(fetchedRange);

        if (apiError) {
          setError(apiError);
        }
      } catch (err) {
        setError("Failed to load sequence data");
      } finally {
        setIsLoadingSequence(false);
      }
    },
    [gene.chrom, genomeId],
  );

  useEffect(() => {
    const initializeGeneData = async () => {
      setIsLoading(true);

      if (!gene.gene_id) {
        setError("Gene ID is missing, cannot fetch details");
        setIsLoading(false);
        return;
      }

      try {
        const {
          geneDetails: fetchedDetail,
          geneBounds: fetchedGeneBounds,
          initialRange: fetchedRange,
        } = await fetchGeneDetails(gene.gene_id);

        setGeneDetail(fetchedDetail);
        setGeneBounds(fetchedGeneBounds);

        if (fetchedRange) {
          setStartPosition(String(fetchedRange.start));
          setEndPosition(String(fetchedRange.end));
          await fetchGeneSequence(fetchedRange.start, fetchedRange.end);
        }
      } catch {
        setError("Faield to load gene information. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    initializeGeneData();
  }, [gene, genomeId]);

  const handleSequenceClick = useCallback(
    (position: number, nucleotide: string) => {
      setActiveSequencePosition(position);
      setActiveReferenceNucleotide(nucleotide);
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (variantAnalysisRef.current) {
        variantAnalysisRef.current.focusAlternativeInput();
      }
    },
    [],
  );

  const handleLoadSequence = useCallback(() => {
    const start = parseInt(startPosition);
    const end = parseInt(endPosition);
    let validationError: string | null = null;

    if (isNaN(start) || isNaN(end)) {
      validationError = "Please enter valid start and end positions";
    } else if (start >= end) {
      validationError = "Start position must be less than end position";
    } else if (geneBounds) {
      const minBound = Math.min(geneBounds.min, geneBounds.max);
      const maxBound = Math.max(geneBounds.min, geneBounds.max);
      if (start < minBound) {
        validationError = `Start position (${start.toLocaleString()}) is below the minimum value (${minBound.toLocaleString()})`;
      } else if (end > maxBound) {
        validationError = `End position (${end.toLocaleString()}) exceeds the maximum value (${maxBound.toLocaleString()})`;
      }

      if (end - start > 10000) {
        validationError = `Selected range exceeds maximum view range of 10.000 bp.`;
      }
    }

    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    fetchGeneSequence(start, end);
  }, [startPosition, endPosition, fetchGeneSequence, geneBounds]);

  const fetchClinvarVariants = async () => {
    if (!gene.chrom || !geneBounds) return;

    setIsLoadingClinvar(true);
    setClinvarError(null);

    try {
      const variants = await apiFetchClinvarVariants(
        gene.chrom,
        geneBounds,
        genomeId,
      );
      setClinvarVariants(variants);
      console.log(variants);
    } catch (error) {
      setClinvarError("Failed to fetch ClinVar variants");
      setClinvarVariants([]);
    } finally {
      setIsLoadingClinvar(false);
    }
  };

  useEffect(() => {
    if (geneBounds) {
      fetchClinvarVariants();
    }
  }, [geneBounds]);

  const showComparison = (variant: ClinvarVariant) => {
    if (variant.evo2Result) {
      setComparisonVariant(variant);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-gray-800"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Back Button & Header */}
      <div className="mb-6">
        <button
          onClick={onClose}
          className="mb-4 flex items-center gap-2 text-sm text-[#3c4f3d]/70 transition-colors hover:text-[#3c4f3d] dark:text-white/70 dark:hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to results
        </button>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-medium text-[#3c4f3d] dark:text-white">
            {gene.symbol}
          </h1>
          <span className="rounded-full bg-white px-3 py-1 text-sm text-[#3c4f3d]/70 dark:bg-[#242924] dark:text-white/70">
            {gene.chrom}
          </span>
        </div>
        <p className="mt-1 text-sm text-[#3c4f3d]/60 dark:text-white/60">
          {gene.name}
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          <VariantAnalysis
            ref={variantAnalysisRef}
            gene={gene}
            genomeId={genomeId}
            chromosome={gene.chrom}
            clinvarVariants={clinvarVariants}
            referenceSequence={activeReferenceNucleotide}
            sequencePosition={activeSequencePosition}
            geneBounds={geneBounds}
            useAfricanAdjustment={useAfricanAdjustment}
            onUseAfricanAdjustmentChange={setUseAfricanAdjustment}
            initialAlt={prefilledAlt}
          />

          <GeneInformation
            gene={gene}
            geneDetail={geneDetail}
            geneBounds={geneBounds}
          />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <KnownVariants
            refreshVariants={fetchClinvarVariants}
            showComparison={showComparison}
            updateClinvarVariant={updateClinvarVariant}
            clinvarVariants={clinvarVariants}
            isLoadingClinvar={isLoadingClinvar}
            clinvarError={clinvarError}
            genomeId={genomeId}
            gene={gene}
            useAfricanAdjustment={useAfricanAdjustment}
          />

          <GeneSequence
            geneBounds={geneBounds}
            geneDetail={geneDetail}
            startPosition={startPosition}
            endPosition={endPosition}
            onStartPositionChange={setStartPosition}
            onEndPositionChange={setEndPosition}
            sequenceData={geneSequence}
            sequenceRange={actualRange}
            isLoading={isLoadingSequence}
            error={error}
            onSequenceLoadRequest={handleLoadSequence}
            onSequenceClick={handleSequenceClick}
            maxViewRange={10000}
          />

          {/* 3D DNA Helix Visualization */}
          {geneSequence && (
            <DNAHelix3D
              sequence={geneSequence}
              mutationPosition={activeSequencePosition}
              referenceBase={activeReferenceNucleotide || undefined}
              alternateBase={prefilledAlt || undefined}
              geneName={gene.symbol}
              startPosition={actualRange?.start}
            />
          )}
        </div>
      </div>

      <VariantComparisonModal
        comparisonVariant={comparisonVariant}
        onClose={() => setComparisonVariant(null)}
        useAfricanAdjustment={useAfricanAdjustment}
      />
    </div>
  );
}
