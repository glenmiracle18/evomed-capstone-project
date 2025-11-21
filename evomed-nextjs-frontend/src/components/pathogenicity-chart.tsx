"use client";

import { useEffect, useState } from "react";
import type { AnalysisResult } from "~/utils/genome-api";

interface PathogenicityChartProps {
  result: AnalysisResult;
}

export function PathogenicityChart({ result }: PathogenicityChartProps) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, [result]);

  const score =
    result.population_adjusted_score ??
    result.evo2_delta_score ??
    result.delta_score ??
    0;
  const confidence =
    (result.confidence ?? result.classification_confidence ?? 0) * 100;

  // Normalize score to 0-100 scale (scores typically range from -10 to +10)
  const normalizedScore = ((score + 10) / 20) * 100;
  const clampedScore = Math.max(0, Math.min(100, normalizedScore));

  // Determine color based on prediction
  const isPathogenic =
    result.prediction?.toLowerCase().includes("pathogenic") &&
    !result.prediction?.toLowerCase().includes("benign");

  const getScoreColor = () => {
    if (isPathogenic) return "#ef4444"; // red
    if (result.prediction?.toLowerCase().includes("uncertain"))
      return "#f59e0b"; // amber
    return "#10b981"; // green
  };

  const getGradientStops = () => {
    if (isPathogenic) {
      return "from-red-500 to-red-600";
    } else if (result.prediction?.toLowerCase().includes("uncertain")) {
      return "from-amber-500 to-amber-600";
    }
    return "from-green-500 to-green-600";
  };

  return (
    <div className="space-y-6">
      {/* Radial Score Visualization */}
      <div className="flex items-center justify-center">
        <div className="relative">
          {/* Background Circle */}
          <svg className="h-48 w-48 -rotate-90 transform">
            <circle
              cx="96"
              cy="96"
              r="88"
              fill="none"
              stroke="#e9eeea"
              strokeWidth="12"
            />
            {/* Animated Progress Circle */}
            <circle
              cx="96"
              cy="96"
              r="88"
              fill="none"
              stroke={getScoreColor()}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 88}`}
              strokeDashoffset={`${2 * Math.PI * 88 * (1 - (animated ? confidence / 100 : 0))}`}
              className="transition-all duration-1000 ease-out"
            />
          </svg>

          {/* Center Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div
              className={`text-4xl font-bold transition-all duration-700 ${animated ? "scale-100 opacity-100" : "scale-0 opacity-0"}`}
              style={{ color: getScoreColor() }}
            >
              {Math.round(confidence)}%
            </div>
            <div className="text-sm text-[#3c4f3d]/70 dark:text-white/70">
              Confidence
            </div>
          </div>
        </div>
      </div>

      {/* Score Bar */}
      <div>
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-[#3c4f3d]/70 dark:text-white/70">
            Delta Score
          </span>
          <span className="font-medium text-[#3c4f3d] dark:text-white">
            {score.toFixed(4)}
          </span>
        </div>

        {/* Score Scale */}
        <div className="relative h-3 w-full overflow-hidden rounded-full bg-[#e9eeea]">
          {/* Gradient background showing scale */}
          <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-amber-500 to-green-500 opacity-20" />

          {/* Midpoint marker */}
          <div className="absolute top-0 left-1/2 h-full w-0.5 bg-[#3c4f3d]/30" />

          {/* Score indicator */}
          <div
            className={`absolute top-0 h-full w-1 bg-gradient-to-b ${getGradientStops()} transition-all duration-1000 ease-out`}
            style={{
              left: animated ? `${clampedScore}%` : "50%",
              transform: "translateX(-50%)",
            }}
          >
            {/* Pointer */}
            <div
              className="absolute -top-1 left-1/2 h-5 w-5 -translate-x-1/2 rotate-45 bg-gradient-to-br"
              style={{ background: getScoreColor() }}
            />
          </div>
        </div>

        <div className="mt-1 flex justify-between text-xs text-[#3c4f3d]/50 dark:text-white">
          <span>Pathogenic</span>
          <span>Neutral</span>
          <span>Benign</span>
        </div>
      </div>

      {/* Prediction Badge */}
      <div className="flex justify-center">
        <div
          className={`transform rounded-lg px-6 py-3 text-center font-medium text-white transition-all duration-700 ${animated ? "scale-100 opacity-100" : "scale-90 opacity-0"} bg-gradient-to-r ${getGradientStops()}`}
        >
          {result.prediction}
        </div>
      </div>

      {/* Additional Metrics */}
      {result.use_african_adjustment && (
        <div className="rounded-lg border border-[#de8246]/20 bg-[#de8246]/5 p-4">
          <div className="mb-2 flex items-center gap-2">
            <svg
              className="h-4 w-4 text-[#de8246]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h5 className="text-sm font-medium text-[#3c4f3d] dark:text-white">
              Population-Adjusted Analysis
            </h5>
          </div>

          {result.african_frequency !== null &&
            result.african_frequency !== undefined && (
              <div className="mt-2">
                <div className="text-xs text-[#3c4f3d]/70 dark:text-white/70">
                  African Population Frequency
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-white">
                    <div
                      className="h-full bg-gradient-to-r from-[#de8246] to-[#de8246]/60 transition-all duration-1000"
                      style={{
                        width: animated
                          ? `${Math.min(result.african_frequency * 100, 100)}%`
                          : "0%",
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-[#3c4f3d] dark:text-white">
                    {(result.african_frequency * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
