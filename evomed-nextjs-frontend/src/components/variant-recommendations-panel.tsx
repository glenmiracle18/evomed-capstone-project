"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Dna, TrendingUp, AlertCircle, Download } from "lucide-react";
import { Button } from "~/components/ui/button";

interface PopulationVariant {
  gene: string;
  variant: string;
  hgvsNotation: string;
  populationFrequency: number;
  pathogenicity: string;
  clinicalSignificance: string;
  cancerRisk: string;
  gnomadId?: string;
}

interface VariantRecommendationsPanelProps {
  variants: PopulationVariant[];
  ancestry: string;
  recommendedGenes: string[];
}

export function VariantRecommendationsPanel({
  variants,
  ancestry,
  recommendedGenes,
}: VariantRecommendationsPanelProps) {
  const [expandedVariant, setExpandedVariant] = useState<string | null>(null);

  const getPathogenicityColor = (pathogenicity: string) => {
    if (pathogenicity.toLowerCase().includes("pathogenic")) {
      return "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200";
    }
    if (pathogenicity.toLowerCase().includes("likely pathogenic")) {
      return "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200";
    }
    return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
  };

  const formatFrequency = (freq: number) => {
    if (freq >= 0.01) {
      return `${(freq * 100).toFixed(2)}%`;
    }
    return `${(freq * 100).toFixed(3)}%`;
  };

  const downloadReport = () => {
    const report = `
GENETIC TESTING RECOMMENDATION REPORT
Generated: ${new Date().toLocaleDateString()}

ANCESTRY: ${ancestry}

RECOMMENDED GENES FOR TESTING:
${recommendedGenes.map((gene, i) => `${i + 1}. ${gene}`).join('\n')}

PRIORITY VARIANTS TO TEST:
${variants.map((v, i) => `
${i + 1}. ${v.gene} - ${v.variant}
   HGVS: ${v.hgvsNotation}
   Population Frequency: ${formatFrequency(v.populationFrequency)}
   Pathogenicity: ${v.pathogenicity}
   Cancer Risk: ${v.cancerRisk}
`).join('\n')}

NOTES:
- This report is for informational purposes only
- Consult with a healthcare provider before genetic testing
- Costs and coverage may vary by insurance and provider
    `.trim();

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `genetic-testing-recommendations-${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-[#3c4f3d] dark:text-white">
              <Dna className="h-5 w-5" />
              Recommended Genetic Variants to Test
            </CardTitle>
            <p className="mt-1 text-sm text-[#3c4f3d]/60 dark:text-white/60">
              Based on your ancestry: <strong>{ancestry}</strong>
            </p>
          </div>
          <Button
            onClick={downloadReport}
            variant="outline"
            size="sm"
            className="border-[#3c4f3d]/20 hover:border-[#de8246] hover:bg-[#de8246]/5 hover:text-[#de8246]"
          >
            <Download className="mr-2 h-4 w-4" />
            Download Report
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Recommended Genes */}
        <div className="rounded-lg border border-[#3c4f3d]/10 bg-[#e9eeea]/50 p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]/50">
          <h4 className="mb-2 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Priority Genes for Testing
          </h4>
          <div className="flex flex-wrap gap-2">
            {recommendedGenes.map((gene) => (
              <Badge
                key={gene}
                className="bg-[#de8246] text-white hover:bg-[#de8246]/90"
              >
                {gene}
              </Badge>
            ))}
          </div>
          <p className="mt-2 text-xs text-[#3c4f3d]/60 dark:text-white/60">
            These genes have the highest-frequency pathogenic variants in your
            population
          </p>
        </div>

        {/* Key Statistics */}
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-3 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
            <div className="text-2xl font-bold text-[#de8246]">
              {variants.length}
            </div>
            <div className="text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Variants to Test
            </div>
          </div>
          <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-3 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
            <div className="text-2xl font-bold text-[#de8246]">
              {recommendedGenes.length}
            </div>
            <div className="text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Priority Genes
            </div>
          </div>
          <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-3 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
            <div className="text-2xl font-bold text-[#de8246]">
              {formatFrequency(
                variants.reduce((sum, v) => sum + v.populationFrequency, 0)
              )}
            </div>
            <div className="text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Total Frequency
            </div>
          </div>
        </div>

        {/* Variants Table */}
        <div>
          <h4 className="mb-3 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Top 20 Variants (Most Common First)
          </h4>
          <div className="overflow-hidden rounded-lg border border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20">
            <div className="max-h-[500px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-[#e9eeea]/50 dark:bg-[#1a1f1a]/50">
                    <TableHead className="text-[#3c4f3d] dark:text-white/70">
                      Gene
                    </TableHead>
                    <TableHead className="text-[#3c4f3d] dark:text-white/70">
                      Variant
                    </TableHead>
                    <TableHead className="text-[#3c4f3d] dark:text-white/70">
                      Frequency
                    </TableHead>
                    <TableHead className="text-[#3c4f3d] dark:text-white/70">
                      Pathogenicity
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {variants.map((variant, index) => (
                    <>
                      <TableRow
                        key={`${variant.gene}-${variant.variant}`}
                        className="cursor-pointer hover:bg-[#e9eeea]/30 dark:hover:bg-[#1a1f1a]/30"
                        onClick={() =>
                          setExpandedVariant(
                            expandedVariant === variant.variant
                              ? null
                              : variant.variant
                          )
                        }
                      >
                        <TableCell className="font-medium text-[#3c4f3d] dark:text-white">
                          <div className="flex items-center gap-2">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#de8246]/10 text-xs font-bold text-[#de8246]">
                              {index + 1}
                            </span>
                            {variant.gene}
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-xs text-[#3c4f3d]/80 dark:text-white/70">
                          {variant.variant}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3 text-[#de8246]" />
                            <span className="text-sm font-medium text-[#3c4f3d] dark:text-white">
                              {formatFrequency(variant.populationFrequency)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={getPathogenicityColor(
                              variant.pathogenicity
                            )}
                          >
                            {variant.pathogenicity}
                          </Badge>
                        </TableCell>
                      </TableRow>
                      {expandedVariant === variant.variant && (
                        <TableRow>
                          <TableCell colSpan={4} className="bg-[#e9eeea]/30 dark:bg-[#1a1f1a]/30">
                            <div className="space-y-2 py-2">
                              <div>
                                <span className="text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                                  HGVS Notation:
                                </span>
                                <p className="font-mono text-xs text-[#3c4f3d] dark:text-white">
                                  {variant.hgvsNotation}
                                </p>
                              </div>
                              <div>
                                <span className="text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                                  Clinical Significance:
                                </span>
                                <p className="text-xs text-[#3c4f3d] dark:text-white">
                                  {variant.clinicalSignificance}
                                </p>
                              </div>
                              <div>
                                <span className="text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                                  Cancer Risk:
                                </span>
                                <p className="text-xs text-[#3c4f3d] dark:text-white">
                                  {variant.cancerRisk}
                                </p>
                              </div>
                              {variant.gnomadId && (
                                <div>
                                  <span className="text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
                                    gnomAD ID:
                                  </span>
                                  <p className="font-mono text-xs text-[#3c4f3d] dark:text-white">
                                    {variant.gnomadId}
                                  </p>
                                </div>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
          <p className="mt-2 text-xs text-[#3c4f3d]/60 dark:text-white/60">
            Click on any row to see more details about the variant
          </p>
        </div>

        {/* Educational Info */}
        <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-950/20">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-blue-900 dark:text-blue-200">
            <AlertCircle className="h-4 w-4" />
            Why These Variants?
          </h4>
          <div className="space-y-1 text-xs leading-relaxed text-blue-900/80 dark:text-blue-200/80">
            <p>
              • These variants are <strong>most common</strong> in your ancestry group
            </p>
            <p>
              • Testing for these specific variants is{" "}
              <strong>20x cheaper</strong> than whole genome sequencing
            </p>
            <p>
              • Targeted testing costs ~$50-100 vs $1000+ for comprehensive
              testing
            </p>
            <p>
              • This approach is ideal for <strong>resource-limited settings</strong>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
