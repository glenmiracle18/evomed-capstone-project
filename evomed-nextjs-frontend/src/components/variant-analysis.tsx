"use client";

import {
  type AnalysisResult,
  analyzeVariantWithAPI,
  type ClinvarVariant,
  type GeneBounds,
  type GeneFromSearch,
} from "~/utils/genome-api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import React, {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import {
  getClassificationColorClasses,
  getNucleotideColorClass,
} from "~/utils/coloring-utils";
import { Button } from "./ui/button";
import { match } from "node:assert";
import { Zap, Globe, Info, HelpCircle } from "lucide-react";
import { Tooltip } from "./ui/tooltip";

export interface VariantAnalysisHandle {
  focusAlternativeInput: () => void;
}

interface VariantAnalysisProps {
  gene: GeneFromSearch;
  genomeId: string;
  chromosome: string;
  clinvarVariants: Array<ClinvarVariant>;
  referenceSequence: string | null;
  sequencePosition: number | null;
  geneBounds: GeneBounds | null;
  useAfricanAdjustment: boolean;
  onUseAfricanAdjustmentChange: (value: boolean) => void;
}

const VariantAnalysis = forwardRef<VariantAnalysisHandle, VariantAnalysisProps>(
  (
    {
      gene,
      genomeId,
      chromosome,
      clinvarVariants = [],
      referenceSequence,
      sequencePosition,
      geneBounds,
      useAfricanAdjustment,
      onUseAfricanAdjustmentChange,
    }: VariantAnalysisProps,
    ref,
  ) => {
    const [variantPosition, setVariantPosition] = useState<string>(
      geneBounds?.min?.toString() || "",
    );
    const [variantReference, setVariantReference] = useState("");
    const [variantAlternative, setVariantAlternative] = useState("");
    const [variantResult, setVariantResult] = useState<AnalysisResult | null>(
      null,
    );
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [variantError, setVariantError] = useState<string | null>(null);
    const alternativeInputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => ({
      focusAlternativeInput: () => {
        if (alternativeInputRef.current) {
          alternativeInputRef.current.focus();
        }
      },
    }));

    useEffect(() => {
      if (sequencePosition && referenceSequence) {
        setVariantPosition(String(sequencePosition));
        setVariantReference(referenceSequence);
      }
    }, [sequencePosition, referenceSequence]);

    const handlePositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setVariantPosition(e.target.value);
      setVariantReference("");
    };

    const handleVariantSubmit = async (pos: string, alt: string) => {
      const position = parseInt(pos);
      if (isNaN(position)) {
        setVariantError("Please enter a valid position number");
        return;
      }

      const validNucleotides = /^[ATGC]$/;
      if (!validNucleotides.test(alt)) {
        setVariantError("Nucleotides must be A, C, G or T");
        return;
      }

      setIsAnalyzing(true);
      setVariantError(null);

      try {
        const data = await analyzeVariantWithAPI({
          position,
          alternative: alt,
          genomeId,
          chromosome,
          useAfricanAdjustment,
        });
        setVariantResult(data);
      } catch (err) {
        console.error(err);
        setVariantError("Failed to analyze variant");
      } finally {
        setIsAnalyzing(false);
      }
    };

    return (
      <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-base font-medium text-[#3c4f3d]">
              Variant Analysis
            </h3>
            <p className="mt-1 text-xs text-[#3c4f3d]/60">
              Predict the impact of genetic variants using the Evo2 deep
              learning model
            </p>
          </div>
          <Tooltip content="Analyze genetic variants using the Evo2 deep learning model. Enter a position and alternative nucleotide to predict the pathogenicity of variants. The model is trained to identify potentially harmful genetic changes." />
        </div>

        {/* African Population Adjustment Toggle */}
        <div className="mb-5 rounded-lg border border-[#3c4f3d]/10 bg-[#e9eeea]/30 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-[#3c4f3d]" />
              <label className="text-sm font-medium text-[#3c4f3d]">
                African Population Adjustment
              </label>
              <Tooltip content="Uses gnomAD African population frequencies to reduce false positives for variants common in African populations" />
            </div>
            <button
              onClick={() =>
                onUseAfricanAdjustmentChange(!useAfricanAdjustment)
              }
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                useAfricanAdjustment ? "bg-[#de8246]" : "bg-[#3c4f3d]/20"
              }`}
              role="switch"
              aria-checked={useAfricanAdjustment}
            >
              <span
                aria-hidden="true"
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white transition duration-200 ease-in-out ${
                  useAfricanAdjustment ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>
          <p className="mt-2 text-xs text-[#3c4f3d]/60">
            {useAfricanAdjustment
              ? "Enabled: Adjusts predictions based on African population frequencies to reduce health disparities"
              : "Disabled: Uses standard Evo2 analysis without population-specific adjustments"}
          </p>
        </div>

        {/* Input Fields */}
        <div className="mb-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium tracking-wider text-[#3c4f3d]/70 uppercase">
                Position
              </label>
              <Input
                value={variantPosition}
                onChange={handlePositionChange}
                className="h-10 border-[#3c4f3d]/20"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium tracking-wider text-[#3c4f3d]/70 uppercase">
                Alternative (variant)
              </label>
              <Input
                ref={alternativeInputRef}
                value={variantAlternative}
                onChange={(e) =>
                  setVariantAlternative(e.target.value.toUpperCase())
                }
                className="h-10 border-[#3c4f3d]/20"
                placeholder="e.g., T"
                maxLength={1}
              />
            </div>
          </div>

          {variantReference && (
            <div className="mt-3 flex items-center gap-2 text-sm text-[#3c4f3d]">
              <span className="text-xs text-[#3c4f3d]/60">Substitution:</span>
              <span
                className={`font-medium ${getNucleotideColorClass(variantReference)}`}
              >
                {variantReference}
              </span>
              <span>→</span>
              <span
                className={`font-medium ${getNucleotideColorClass(variantAlternative)}`}
              >
                {variantAlternative ? variantAlternative : "?"}
              </span>
            </div>
          )}

          <Button
            disabled={isAnalyzing || !variantPosition || !variantAlternative}
            className="mt-4 h-10 w-full cursor-pointer bg-[#3c4f3d] text-white hover:bg-[#3c4f3d]/90"
            onClick={() =>
              handleVariantSubmit(
                variantPosition.replaceAll(",", ""),
                variantAlternative,
              )
            }
          >
            {isAnalyzing ? (
              <>
                <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                Analyzing...
              </>
            ) : (
              "Analyze variant"
            )}
          </Button>
        </div>

        {variantPosition &&
          clinvarVariants
            .filter(
              (variant) =>
                variant?.variation_type
                  ?.toLowerCase()
                  .includes("single nucleotide") &&
                parseInt(variant?.location?.replaceAll(",", "")) ===
                  parseInt(variantPosition.replaceAll(",", "")),
            )
            .map((matchedVariant) => {
              const refAltMatch = matchedVariant.title.match(/(\w)>(\w)/);

              let ref = null;
              let alt = null;
              if (refAltMatch && refAltMatch.length === 3) {
                ref = refAltMatch[1];
                alt = refAltMatch[2];
              }

              if (!ref || !alt) return null;

              return (
                <div
                  key={matchedVariant.clinvar_id}
                  className="border-priamry/10 mt-4 rounded-md border bg-[#e9eeea]/30 p-4"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <h4 className="text-priamry text-sm font-medium">
                      Known Variant Detected
                    </h4>
                    <span className="text-priamry/70 text-xs">
                      Position: {matchedVariant.location}
                    </span>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <div className="text-priamry/70 mb-1 text-xs font-medium">
                        Variant Details
                      </div>
                      <div className="text-sm">{matchedVariant.title}</div>
                      <div className="mt-2 text-sm">
                        {gene?.symbol} {variantPosition}{" "}
                        <span className="font-mono">
                          <span className={getNucleotideColorClass(ref)}>
                            {ref}
                          </span>
                          <span>{">"}</span>
                          <span className={getNucleotideColorClass(alt)}>
                            {alt}
                          </span>
                        </span>
                      </div>
                      <div className="text-priamry/70 mt-2 text-xs">
                        ClinVar classification
                        <span
                          className={`ml-1 rounded-sm px-2 py-0.5 ${getClassificationColorClasses(matchedVariant.classification)}`}
                        >
                          {matchedVariant.classification || "Unknown"}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-end">
                      <Button
                        disabled={isAnalyzing}
                        variant="outline"
                        size="sm"
                        className="border-priamry text-priamry hover:bg-priamry/10 bg-secondary h-7 cursor-pointer text-xs"
                        onClick={() => {
                          setVariantAlternative(alt);
                          handleVariantSubmit(
                            variantPosition.replaceAll(",", ""),
                            alt,
                          );
                        }}
                      >
                        {isAnalyzing ? (
                          <>
                            <span className="mr-1 inline-block h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent align-middle"></span>
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Zap className="mr-1 inline-block h-3 w-3" />
                            Analyze this Variant
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })[0]}
        {variantError && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {variantError}
          </div>
        )}

        {variantResult && (
          <div className="mt-6 space-y-4">
            {/* Main Result Card */}
            <div className="border-priamry/10 rounded-lg border bg-[#e9eeea]/30 p-4">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="text-priamry text-sm font-medium">
                  Analysis Result
                </h4>
                {variantResult.use_african_adjustment && (
                  <div className="text-priamry/70 flex items-center gap-1 text-xs">
                    <Globe className="h-3 w-3" />
                    <span>African Population Adjusted</span>
                  </div>
                )}
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <div className="mb-3">
                    <div className="text-priamry/70 text-xs font-medium">
                      Variant
                    </div>
                    <div className="text-sm">
                      {gene?.symbol} {variantResult.position}{" "}
                      <span className="font-mono">
                        <span
                          className={getNucleotideColorClass(
                            variantResult.reference,
                          )}
                        >
                          {variantResult.reference}
                        </span>
                        {">"}
                        <span
                          className={getNucleotideColorClass(
                            variantResult.alternative,
                          )}
                        >
                          {variantResult.alternative}
                        </span>
                      </span>
                    </div>
                  </div>

                  {/* Score Display */}
                  <div className="space-y-2">
                    {variantResult.use_african_adjustment &&
                    variantResult.evo2_delta_score !== undefined ? (
                      <>
                        <div>
                          <div className="text-priamry/70 text-xs font-medium">
                            Original Evo2 Score
                          </div>
                          <div className="font-mono text-sm">
                            {variantResult.evo2_delta_score.toFixed(6)}
                          </div>
                        </div>
                        <div>
                          <div className="text-priamry/70 text-xs font-medium">
                            Population-Adjusted Score
                          </div>
                          <div className="font-mono text-sm">
                            {variantResult.population_adjusted_score?.toFixed(
                              6,
                            )}
                            {variantResult.population_adjustment !== 0 && (
                              <span
                                className={`ml-2 text-xs ${
                                  (variantResult.population_adjustment || 0) > 0
                                    ? "text-green-600"
                                    : "text-red-600"
                                }`}
                              >
                                (
                                {(variantResult.population_adjustment || 0) > 0
                                  ? "+"
                                  : ""}
                                {variantResult.population_adjustment?.toFixed(
                                  6,
                                )}
                                )
                              </span>
                            )}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Delta Likelihood Score
                        </div>
                        <div className="font-mono text-sm">
                          {(
                            variantResult.delta_score ||
                            variantResult.evo2_delta_score
                          )?.toFixed(6)}
                        </div>
                      </div>
                    )}
                    <div className="text-priamry/60 text-xs">
                      Negative score indicates loss of function
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-priamry/70 text-xs font-medium">
                    Prediction
                  </div>
                  <div
                    className={`inline-block rounded-lg px-3 py-1 text-xs ${getClassificationColorClasses(variantResult.prediction)}`}
                  >
                    {variantResult.prediction}
                  </div>

                  {/* Classification Method */}
                  {variantResult.classification_method && (
                    <div className="mt-2">
                      <div className="text-priamry/70 text-xs font-medium">
                        Method
                      </div>
                      <div className="text-priamry/80 text-xs">
                        {variantResult.classification_method
                          .replace(/_/g, " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </div>
                    </div>
                  )}

                  <div className="mt-3">
                    <div className="text-priamry/70 text-xs font-medium">
                      Confidence
                    </div>
                    <div className="mt-1 h-2 w-full rounded-full bg-[#e9eeea]">
                      <div
                        className={`h-2 rounded-full ${variantResult.prediction.includes("pathogenic") ? "bg-red-600" : "bg-green-600"}`}
                        style={{
                          width: `${Math.min(100, (variantResult.confidence || variantResult.classification_confidence || 0) * 100)}%`,
                        }}
                      ></div>
                    </div>
                    <div className="text-priamry/60 mt-1 text-right text-xs">
                      {Math.round(
                        (variantResult.confidence ||
                          variantResult.classification_confidence ||
                          0) * 100,
                      )}
                      %
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Genomic Location Context Card (NEW) */}
            {variantResult.location_context && (
              <div className="rounded-lg border border-[#3c4f3d]/20 bg-[#3c4f3d]/5 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <Info className="h-4 w-4 text-[#3c4f3d]" />
                  <h5 className="text-priamry text-sm font-medium">
                    Genomic Location & Context
                  </h5>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    {variantResult.gene_symbol && (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Gene
                        </div>
                        <div className="text-sm font-medium">
                          {variantResult.gene_symbol}
                        </div>
                      </div>
                    )}

                    {variantResult.region_type && (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Region Type
                        </div>
                        <div className="text-sm">
                          <span
                            className={`inline-block rounded px-2 py-0.5 text-xs ${
                              variantResult.is_coding
                                ? "bg-blue-100 text-blue-800"
                                : variantResult.region_type === "regulatory"
                                  ? "bg-purple-100 text-purple-800"
                                  : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {variantResult.region_type.replace(/_/g, " ")}
                            {variantResult.is_coding
                              ? " (coding)"
                              : " (non-coding)"}
                          </span>
                        </div>
                      </div>
                    )}

                    {variantResult.impact && (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Predicted Impact
                        </div>
                        <div className="text-sm">
                          <span
                            className={`inline-block rounded px-2 py-0.5 text-xs ${
                              variantResult.impact === "HIGH"
                                ? "bg-red-100 text-red-800"
                                : variantResult.impact === "MODERATE"
                                  ? "bg-orange-100 text-orange-800"
                                  : variantResult.impact === "LOW"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {variantResult.impact}
                          </span>
                        </div>
                      </div>
                    )}

                    {variantResult.consequence_terms &&
                      variantResult.consequence_terms.length > 0 && (
                        <div>
                          <div className="text-priamry/70 text-xs font-medium">
                            Consequence Terms
                          </div>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {variantResult.consequence_terms.map(
                              (term, idx) => (
                                <span
                                  key={idx}
                                  className="inline-block rounded bg-[#e9eeea] px-2 py-0.5 text-xs text-[#3c4f3d]"
                                >
                                  {term.replace(/_/g, " ")}
                                </span>
                              ),
                            )}
                          </div>
                        </div>
                      )}
                  </div>

                  <div>
                    {variantResult.location_context && (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Context Description
                        </div>
                        <div className="text-priamry/90 text-sm leading-relaxed">
                          {variantResult.location_context}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* African Population Information Card */}
            {variantResult.use_african_adjustment && (
              <div className="rounded-lg border border-[#de8246]/20 bg-[#de8246]/5 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <Globe className="h-4 w-4 text-[#de8246]" />
                  <h5 className="text-priamry text-sm font-medium">
                    African Population Context
                  </h5>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <div className="space-y-2">
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          African Population Frequency
                        </div>
                        <div className="text-sm">
                          {variantResult.african_frequency !== null &&
                          variantResult.african_frequency !== undefined
                            ? `${(variantResult.african_frequency * 100).toFixed(4)}% (${variantResult.african_frequency.toFixed(6)})`
                            : "Not found in gnomAD African populations"}
                        </div>
                      </div>

                      {variantResult.global_frequency !== null &&
                        variantResult.global_frequency !== undefined && (
                          <div>
                            <div className="text-priamry/70 text-xs font-medium">
                              Global Population Frequency
                            </div>
                            <div className="text-sm">
                              {(variantResult.global_frequency * 100).toFixed(
                                4,
                              )}
                              % ({variantResult.global_frequency.toFixed(6)})
                            </div>
                          </div>
                        )}

                      {/* NEW: Data Sources Indicator */}
                      {variantResult.data_sources && (
                        <div className="mt-2">
                          <div className="text-priamry/70 text-xs font-medium">
                            Data Sources
                          </div>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {variantResult.data_sources.gnomad && (
                              <span className="inline-block rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-800">
                                gnomAD
                              </span>
                            )}
                            {variantResult.data_sources["1000genomes"] && (
                              <span className="inline-block rounded bg-green-100 px-2 py-0.5 text-xs text-green-800">
                                1000 Genomes
                              </span>
                            )}
                            {variantResult.data_sources.ensembl_vep && (
                              <span className="inline-block rounded bg-purple-100 px-2 py-0.5 text-xs text-purple-800">
                                Ensembl VEP
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    {variantResult.frequency_context && (
                      <div>
                        <div className="text-priamry/70 text-xs font-medium">
                          Frequency Context
                        </div>
                        <div className="text-priamry/90 text-sm leading-relaxed">
                          {variantResult.frequency_context}
                        </div>
                      </div>
                    )}

                    {variantResult.adjustment_reasoning && (
                      <div className="mt-2">
                        <div className="text-priamry/70 text-xs font-medium">
                          Adjustment Reasoning
                        </div>
                        <div className="text-priamry/90 text-sm leading-relaxed">
                          {variantResult.adjustment_reasoning}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Health Equity Notice */}
                {variantResult.african_frequency &&
                  variantResult.african_frequency > 0.01 && (
                    <div className="mt-3 rounded border border-green-200 bg-green-50 p-2">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                        <div className="text-xs text-green-800">
                          <strong>Health Equity Note:</strong> This variant is
                          common in African populations. Population-specific
                          analysis helps reduce false positive pathogenic
                          classifications.
                        </div>
                      </div>
                    </div>
                  )}
              </div>
            )}

            {/* NEW: Clinical Interpretation Card */}
            {variantResult.clinical_interpretation && (
              <div className="rounded-lg border border-[#3c4f3d]/20 bg-white p-4">
                <div className="mb-2 flex items-center gap-2">
                  <HelpCircle className="h-4 w-4 text-[#3c4f3d]" />
                  <h5 className="text-priamry text-sm font-medium">
                    Clinical Interpretation
                  </h5>
                </div>
                <div className="text-priamry/90 text-sm leading-relaxed">
                  {variantResult.clinical_interpretation}
                </div>
                {variantResult.threshold_description && (
                  <div className="text-priamry/60 mt-2 text-xs">
                    Threshold applied: {variantResult.threshold_description}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  },
);

export default VariantAnalysis;
