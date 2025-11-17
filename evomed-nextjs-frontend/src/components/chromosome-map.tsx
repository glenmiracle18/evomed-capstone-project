"use client";

import { useState } from "react";

interface ChromosomeMapProps {
  chromosomes: Array<{ name: string; size?: number }>;
  selectedChromosome: string;
  onSelectChromosome: (chrom: string) => void;
}

export function ChromosomeMap({
  chromosomes,
  selectedChromosome,
  onSelectChromosome,
}: ChromosomeMapProps) {
  const [hoveredChrom, setHoveredChrom] = useState<string | null>(null);

  // Approximate relative sizes for human chromosomes (in Mbp)
  const chromosomeSizes: Record<string, number> = {
    chr1: 248, chr2: 242, chr3: 198, chr4: 190, chr5: 181,
    chr6: 170, chr7: 159, chr8: 145, chr9: 138, chr10: 133,
    chr11: 135, chr12: 133, chr13: 114, chr14: 107, chr15: 102,
    chr16: 90, chr17: 83, chr18: 80, chr19: 58, chr20: 64,
    chr21: 46, chr22: 50, chrX: 156, chrY: 57,
  };

  const maxSize = Math.max(...Object.values(chromosomeSizes));

  return (
    <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:bg-[#242924]">
      <div className="mb-3">
        <h4 className="text-sm font-medium text-[#3c4f3d] dark:text-white">Chromosome Map</h4>
        <p className="text-xs text-[#3c4f3d]/60 dark:text-white/60">Click a chromosome to browse genes</p>
      </div>

      {/* Chromosome Visualization */}
      <div className="relative">
        <div className="grid grid-cols-12 gap-2">
          {chromosomes.slice(0, 24).map((chrom) => {
            const size = chromosomeSizes[chrom.name] || 100;
            const heightPercentage = (size / maxSize) * 100;
            const isSelected = chrom.name === selectedChromosome;
            const isHovered = chrom.name === hoveredChrom;

            return (
              <button
                key={chrom.name}
                onClick={() => onSelectChromosome(chrom.name)}
                onMouseEnter={() => setHoveredChrom(chrom.name)}
                onMouseLeave={() => setHoveredChrom(null)}
                className="group relative flex flex-col items-center"
              >
                {/* Chromosome Bar */}
                <div
                  className={`relative w-full rounded-full transition-all duration-300 ${
                    isSelected
                      ? "bg-[#de8246]"
                      : isHovered
                        ? "bg-[#3c4f3d]/60"
                        : "bg-[#3c4f3d]/20"
                  }`}
                  style={{
                    height: `${Math.max(heightPercentage, 30)}px`,
                  }}
                >
                  {/* Centromere band (approximate middle) */}
                  <div
                    className={`absolute left-0 right-0 h-1.5 rounded-full transition-all ${
                      isSelected
                        ? "bg-[#de8246]/50"
                        : "bg-[#3c4f3d]/40"
                    }`}
                    style={{
                      top: "45%",
                    }}
                  />

                  {/* Hover tooltip */}
                  {isHovered && (
                    <div className="absolute -top-8 left-1/2 z-10 -translate-x-1/2 whitespace-nowrap rounded bg-[#3c4f3d] px-2 py-1 text-xs text-white">
                      {size} Mbp
                    </div>
                  )}
                </div>

                {/* Label */}
                <span
                  className={`mt-1.5 text-xs font-medium transition-colors ${
                    isSelected
                      ? "text-[#de8246]"
                      : "text-[#3c4f3d]/70 dark:text-white/70 group-hover:text-[#3c4f3d] dark:text-white"
                  }`}
                >
                  {chrom.name.replace("chr", "")}
                </span>
              </button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-4 flex items-center justify-center gap-4 text-xs text-[#3c4f3d]/60 dark:text-white/60">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-[#de8246]"></div>
            <span>Selected</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-[#3c4f3d]/20"></div>
            <span>Available</span>
          </div>
        </div>
      </div>
    </div>
  );
}
