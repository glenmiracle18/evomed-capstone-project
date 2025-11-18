"use client";

import { useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";

interface AfricaAncestryMapProps {
  selectedAncestry: string;
  onAncestrySelect: (ancestry: string) => void;
}

// Map countries to regions and ancestries
const COUNTRY_TO_REGION: Record<string, string> = {
  // North Africa
  "Egypt": "north-africa",
  "Libya": "north-africa",
  "Tunisia": "north-africa",
  "Algeria": "north-africa",
  "Morocco": "north-africa",
  "Western Sahara": "north-africa",

  // West Africa
  "Nigeria": "west-africa",
  "Ghana": "west-africa",
  "Senegal": "west-africa",
  "Mali": "west-africa",
  "Burkina Faso": "west-africa",
  "Niger": "west-africa",
  "Ivory Coast": "west-africa",
  "Côte d'Ivoire": "west-africa",
  "Guinea": "west-africa",
  "Benin": "west-africa",
  "Togo": "west-africa",
  "Sierra Leone": "west-africa",
  "Liberia": "west-africa",
  "Mauritania": "west-africa",
  "Gambia": "west-africa",
  "Guinea-Bissau": "west-africa",

  // East Africa
  "Kenya": "east-africa",
  "Ethiopia": "east-africa",
  "Somalia": "east-africa",
  "Tanzania": "east-africa",
  "Uganda": "east-africa",
  "Rwanda": "east-africa",
  "Burundi": "east-africa",
  "Eritrea": "east-africa",
  "Djibouti": "east-africa",
  "South Sudan": "east-africa",

  // Cameroon (Separate region for country focus)
  "Cameroon": "cameroon",

  // Central Africa
  "Democratic Republic of the Congo": "central-africa",
  "Dem. Rep. Congo": "central-africa",
  "Congo": "central-africa",
  "Central African Republic": "central-africa",
  "Chad": "central-africa",
  "Gabon": "central-africa",
  "Equatorial Guinea": "central-africa",

  // South Africa
  "South Africa": "south-africa",
  "Namibia": "south-africa",
  "Botswana": "south-africa",
  "Zimbabwe": "south-africa",
  "Zambia": "south-africa",
  "Mozambique": "south-africa",
  "Malawi": "south-africa",
  "Angola": "south-africa",
  "Lesotho": "south-africa",
  "Swaziland": "south-africa",
  "Eswatini": "south-africa",
  "Madagascar": "south-africa",
};

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
  "cameroon": [
    { value: "cameroon-bamileke", label: "Bamileke (West Region)" },
    { value: "cameroon-fulani", label: "Fulani/Fulbe (North)" },
    { value: "cameroon-beti", label: "Beti-Pahuin (Centre/South)" },
    { value: "cameroon-duala", label: "Duala (Littoral)" },
    { value: "cameroon-bassa", label: "Bassa (Littoral)" },
    { value: "cameroon-bamoun", label: "Bamoun (West)" },
    { value: "cameroon-other", label: "Other Cameroonian" },
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

const REGION_LABELS: Record<string, string> = {
  "north-africa": "North Africa",
  "west-africa": "West Africa",
  "east-africa": "East Africa",
  "cameroon": "Cameroon",
  "central-africa": "Central Africa",
  "south-africa": "Southern Africa",
};

// TopoJSON URL for world map (we'll filter for Africa)
const WORLD_TOPO_JSON = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

export function AfricaAncestryMap({ selectedAncestry, onAncestrySelect }: AfricaAncestryMapProps) {
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null);
  const [showRegionOptions, setShowRegionOptions] = useState<string | null>(null);
  const [tooltipContent, setTooltipContent] = useState<string>("");

  const getRegionFromCountry = (countryName: string): string | null => {
    return COUNTRY_TO_REGION[countryName] || null;
  };

  const getSelectedRegion = (): string | null => {
    for (const [region, ancestries] of Object.entries(REGION_TO_ANCESTRY)) {
      if (ancestries.some(a => a.value === selectedAncestry)) {
        return region;
      }
    }
    return null;
  };

  const handleCountryClick = (geo: any) => {
    const countryName = geo.properties.name;
    const region = getRegionFromCountry(countryName);

    if (!region) return;

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

  const getCountryFill = (geo: any): string => {
    const countryName = geo.properties.name;
    const region = getRegionFromCountry(countryName);
    const selectedRegion = getSelectedRegion();

    if (!region) return "#f0f0f0"; // Non-African countries

    if (region === selectedRegion) return "#de8246"; // Selected region (brand orange)
    if (hoveredCountry === countryName) return "#3c4f3d"; // Hovered (brand dark green)

    return "#e9eeea"; // Default (brand light background)
  };

  return (
    <div className="relative">
      {/* Map Container */}
      <div className="rounded-lg border border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 bg-white dark:bg-[#242924] p-4">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 400,
            center: [20, 0], // Center on Africa
          }}
          width={800}
          height={600}
          className="w-full h-auto"
        >
          <ZoomableGroup center={[20, 0]} zoom={1}>
            <Geographies geography={WORLD_TOPO_JSON}>
              {({ geographies }) =>
                geographies
                  .filter(geo => COUNTRY_TO_REGION[geo.properties.name])
                  .map((geo) => {
                    const countryName = geo.properties.name;
                    const region = getRegionFromCountry(countryName);

                    return (
                      <Geography
                        key={geo.rsmKey}
                        geography={geo}
                        fill={getCountryFill(geo)}
                        stroke="#3c4f3d"
                        strokeWidth={0.5}
                        style={{
                          default: { outline: "none" },
                          hover: { outline: "none", cursor: "pointer" },
                          pressed: { outline: "none" },
                        }}
                        onMouseEnter={() => {
                          setHoveredCountry(countryName);
                          const regionLabel = region ? REGION_LABELS[region] : "";
                          setTooltipContent(`${countryName}${regionLabel ? ` (${regionLabel})` : ""}`);
                        }}
                        onMouseLeave={() => {
                          setHoveredCountry(null);
                          setTooltipContent("");
                        }}
                        onClick={() => handleCountryClick(geo)}
                      />
                    );
                  })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

        {/* Tooltip */}
        {tooltipContent && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-[#3c4f3d] text-white px-3 py-1.5 rounded-md text-sm shadow-lg pointer-events-none z-10">
            {tooltipContent}
          </div>
        )}
      </div>

      {/* Region Options Popup */}
      {showRegionOptions && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/20 rounded-lg backdrop-blur-sm z-20">
          <div className="bg-white dark:bg-[#242924] rounded-lg p-4 shadow-xl border border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 max-w-xs w-full mx-4">
            <h3 className="text-sm font-semibold text-[#3c4f3d] dark:text-white mb-3">
              Select Your Ancestry in {REGION_LABELS[showRegionOptions]}
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
      <div className="mt-4 space-y-2">
        <div className="text-xs text-[#3c4f3d]/60 dark:text-white/60 text-center">
          Click on any African country to select your ancestry
        </div>
        <div className="flex items-center justify-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-[#de8246]"></div>
            <span className="text-[#3c4f3d]/60 dark:text-white/60">Selected Region</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-[#3c4f3d]"></div>
            <span className="text-[#3c4f3d]/60 dark:text-white/60">Hover</span>
          </div>
        </div>
      </div>
    </div>
  );
}
