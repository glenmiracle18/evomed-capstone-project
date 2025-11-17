import type {
  GeneBounds,
  GeneDetailsFromSearch,
  GeneFromSearch,
} from "~/utils/genome-api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ExternalLink, HelpCircle } from "lucide-react";
import { Tooltip } from "./ui/tooltip";

export function GeneInformation({
  gene,
  geneDetail,
  geneBounds,
}: {
  gene: GeneFromSearch;
  geneDetail: GeneDetailsFromSearch | null;
  geneBounds: GeneBounds | null;
}) {
  return (
    <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-5 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-base font-medium text-[#3c4f3d] dark:text-white">
            Gene Information
          </h3>
          <Tooltip content="Basic information about this gene including its symbol, full name, location on the chromosome, and links to external databases. This data comes from genomic reference databases and provides context about the gene's function and characteristics." />
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid gap-3 text-sm">
          <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
            <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">Symbol</span>
            <span className="flex-1 text-[#3c4f3d] dark:text-white">{gene.symbol}</span>
          </div>

          <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
            <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">Name</span>
            <span className="flex-1 text-[#3c4f3d] dark:text-white">{gene.name}</span>
          </div>

          {gene.description && gene.description !== gene.name && (
            <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
              <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">
                Description
              </span>
              <span className="flex-1 text-[#3c4f3d] dark:text-white">{gene.description}</span>
            </div>
          )}

          <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
            <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">
              Chromosome
            </span>
            <span className="flex-1 text-[#3c4f3d] dark:text-white">{gene.chrom}</span>
          </div>

          {geneBounds && (
            <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
              <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">
                Position
              </span>
              <span className="flex-1 text-[#3c4f3d] dark:text-white">
                {Math.min(geneBounds.min, geneBounds.max).toLocaleString()} -{" "}
                {Math.max(geneBounds.min, geneBounds.max).toLocaleString()} (
                {Math.abs(geneBounds.max - geneBounds.min + 1).toLocaleString()}{" "}
                bp)
                {geneDetail?.genomicinfo?.[0]?.strand === "-" &&
                  " (reverse strand)"}
              </span>
            </div>
          )}

          {gene.gene_id && (
            <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
              <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">
                Gene ID
              </span>
              <span className="flex-1">
                <a
                  href={`https://www.ncbi.nlm.nih.gov/gene/${gene.gene_id}`}
                  target="_blank"
                  className="flex items-center text-[#de8246] hover:text-[#de8246]/80"
                >
                  {gene.gene_id}
                  <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </span>
            </div>
          )}

          {geneDetail?.organism && (
            <div className="flex items-start border-b border-[#3c4f3d]/5 pb-2">
              <span className="w-32 font-medium text-[#3c4f3d]/70 dark:text-white/70">
                Organism
              </span>
              <span className="flex-1 text-[#3c4f3d] dark:text-white">
                {geneDetail.organism.scientificname}
                {geneDetail.organism.commonname &&
                  ` (${geneDetail.organism.commonname})`}
              </span>
            </div>
          )}
        </div>

        {geneDetail?.summary && (
          <div className="mt-4 rounded-lg bg-[#e9eeea]/30 dark:bg-[#1a1f1a]/50 p-4">
            <h4 className="mb-2 text-sm font-medium text-[#3c4f3d] dark:text-white">Summary</h4>
            <p className="text-sm leading-relaxed text-[#3c4f3d]/80">
              {geneDetail.summary}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
