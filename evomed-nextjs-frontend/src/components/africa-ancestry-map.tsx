"use client";

import { useState } from "react";

interface AfricaAncestryMapProps {
  selectedAncestry: string;
  onAncestrySelect: (ancestry: string) => void;
}

// Map regions to ancestry values
const REGION_TO_ANCESTRY: Record<string, { value: string; label: string }[]> = {
  "north-africa": [
    { value: "north-african-egyptian", label: "Egyptian" },
    { value: "north-african-moroccan", label: "Moroccan" },
  ],
  "west-africa": [
    { value: "west-african-yoruba", label: "Yoruba (Nigeria)" },
    { value: "west-african-akan", label: "Akan (Ghana)" },
    { value: "west-african-igbo", label: "Igbo (Nigeria)" },
    { value: "west-african-hausa", label: "Hausa (Nigeria/Niger)" },
  ],
  "east-africa": [
    { value: "east-african-kikuyu", label: "Kikuyu (Kenya)" },
    { value: "east-african-luo", label: "Luo (Kenya)" },
    { value: "east-african-ethiopian", label: "Ethiopian" },
    { value: "east-african-somali", label: "Somali" },
  ],
  "central-africa": [
    { value: "central-african-bantu", label: "Bantu" },
  ],
  "south-africa": [
    { value: "south-african-zulu", label: "Zulu" },
    { value: "south-african-xhosa", label: "Xhosa" },
    { value: "south-african-sotho", label: "Sotho" },
  ],
};

export function AfricaAncestryMap({ selectedAncestry, onAncestrySelect }: AfricaAncestryMapProps) {
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null);
  const [showRegionOptions, setShowRegionOptions] = useState<string | null>(null);

  const handleRegionClick = (region: string) => {
    const options = REGION_TO_ANCESTRY[region];
    if (options && options.length === 1) {
      // If only one option, select it directly
      onAncestrySelect(options[0].value);
      setShowRegionOptions(null);
    } else if (options && options.length > 1) {
      // If multiple options, show selection menu
      setShowRegionOptions(region);
    }
  };

  const getRegionColor = (region: string) => {
    const options = REGION_TO_ANCESTRY[region];
    const isSelected = options?.some(opt => opt.value === selectedAncestry);
    const isHovered = hoveredRegion === region;

    if (isSelected) return "#de8246"; // Brand orange
    if (isHovered) return "#3c4f3d"; // Brand dark green
    return "#e9eeea"; // Default light background
  };

  const getRegionStroke = (region: string) => {
    const options = REGION_TO_ANCESTRY[region];
    const isSelected = options?.some(opt => opt.value === selectedAncestry);
    return isSelected ? "#de8246" : "#3c4f3d";
  };

  return (
    <div className="relative">
      {/* SVG Map */}
      <svg
        viewBox="0 0 800 900"
        className="w-full max-w-2xl mx-auto"
        style={{ maxHeight: "500px" }}
      >
        {/* North Africa */}
        <path
          d="M 100,100 L 700,100 L 700,250 L 100,250 Z"
          fill={getRegionColor("north-africa")}
          stroke={getRegionStroke("north-africa")}
          strokeWidth="2"
          className="cursor-pointer transition-all duration-200"
          onMouseEnter={() => setHoveredRegion("north-africa")}
          onMouseLeave={() => setHoveredRegion(null)}
          onClick={() => handleRegionClick("north-africa")}
        />
        <text
          x="400"
          y="175"
          textAnchor="middle"
          className="fill-[#3c4f3d] dark:fill-white text-sm font-medium pointer-events-none"
        >
          North Africa
        </text>

        {/* West Africa */}
        <path
          d="M 100,250 L 400,250 L 400,500 L 100,500 Z"
          fill={getRegionColor("west-africa")}
          stroke={getRegionStroke("west-africa")}
          strokeWidth="2"
          className="cursor-pointer transition-all duration-200"
          onMouseEnter={() => setHoveredRegion("west-africa")}
          onMouseLeave={() => setHoveredRegion(null)}
          onClick={() => handleRegionClick("west-africa")}
        />
        <text
          x="250"
          y="375"
          textAnchor="middle"
          className="fill-[#3c4f3d] dark:fill-white text-sm font-medium pointer-events-none"
        >
          West Africa
        </text>

        {/* Central Africa */}
        <path
          d="M 400,250 L 550,250 L 550,500 L 400,500 Z"
          fill={getRegionColor("central-africa")}
          stroke={getRegionStroke("central-africa")}
          strokeWidth="2"
          className="cursor-pointer transition-all duration-200"
          onMouseEnter={() => setHoveredRegion("central-africa")}
          onMouseLeave={() => setHoveredRegion(null)}
          onClick={() => handleRegionClick("central-africa")}
        />
        <text
          x="475"
          y="375"
          textAnchor="middle"
          className="fill-[#3c4f3d] dark:fill-white text-sm font-medium pointer-events-none"
        >
          Central
        </text>

        {/* East Africa */}
        <path
          d="M 550,250 L 700,250 L 700,500 L 550,500 Z"
          fill={getRegionColor("east-africa")}
          stroke={getRegionStroke("east-africa")}
          strokeWidth="2"
          className="cursor-pointer transition-all duration-200"
          onMouseEnter={() => setHoveredRegion("east-africa")}
          onMouseLeave={() => setHoveredRegion(null)}
          onClick={() => handleRegionClick("east-africa")}
        />
        <text
          x="625"
          y="375"
          textAnchor="middle"
          className="fill-[#3c4f3d] dark:fill-white text-sm font-medium pointer-events-none"
        >
          East Africa
        </text>

        {/* South Africa */}
        <path
          d="M 250,500 L 550,500 L 550,700 L 250,700 Z"
          fill={getRegionColor("south-africa")}
          stroke={getRegionStroke("south-africa")}
          strokeWidth="2"
          className="cursor-pointer transition-all duration-200"
          onMouseEnter={() => setHoveredRegion("south-africa")}
          onMouseLeave={() => setHoveredRegion(null)}
          onClick={() => handleRegionClick("south-africa")}
        />
        <text
          x="400"
          y="600"
          textAnchor="middle"
          className="fill-[#3c4f3d] dark:fill-white text-sm font-medium pointer-events-none"
        >
          South Africa
        </text>
      </svg>

      {/* Region Options Popup */}
      {showRegionOptions && (
        <div className="absolute top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black/20 rounded-lg backdrop-blur-sm">
          <div className="bg-white dark:bg-[#242924] rounded-lg p-4 shadow-xl border border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 max-w-xs w-full mx-4">
            <h3 className="text-sm font-semibold text-[#3c4f3d] dark:text-white mb-3">
              Select Your Ancestry
            </h3>
            <div className="space-y-2">
              {REGION_TO_ANCESTRY[showRegionOptions]?.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    onAncestrySelect(option.value);
                    setShowRegionOptions(null);
                  }}
                  className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-[#de8246]/10 text-[#3c4f3d] dark:text-white transition-colors"
                >
                  {option.label}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowRegionOptions(null)}
              className="mt-3 w-full px-3 py-2 text-sm text-[#3c4f3d]/60 dark:text-white/60 hover:text-[#3c4f3d] dark:hover:text-white transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 text-xs text-[#3c4f3d]/60 dark:text-white/60 text-center">
        Click on a region to select your ancestry
      </div>
    </div>
  );
}
