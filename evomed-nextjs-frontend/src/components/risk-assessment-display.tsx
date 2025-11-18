"use client";

import { AlertTriangle, CheckCircle, Info, AlertCircle } from "lucide-react";

interface RiskAssessment {
  riskScore: number;
  riskLevel: "Low" | "Moderate" | "High" | "Very High";
  explanation: string;
  factors: string[];
}

interface RiskAssessmentDisplayProps {
  riskAssessment: RiskAssessment;
}

export function RiskAssessmentDisplay({
  riskAssessment,
}: RiskAssessmentDisplayProps) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case "Very High":
        return {
          bg: "bg-red-50 dark:bg-red-950/20",
          border: "border-red-200 dark:border-red-900",
          text: "text-red-900 dark:text-red-200",
          icon: "text-red-600 dark:text-red-400",
          progress: "bg-red-600",
        };
      case "High":
        return {
          bg: "bg-orange-50 dark:bg-orange-950/20",
          border: "border-orange-200 dark:border-orange-900",
          text: "text-orange-900 dark:text-orange-200",
          icon: "text-orange-600 dark:text-orange-400",
          progress: "bg-orange-600",
        };
      case "Moderate":
        return {
          bg: "bg-amber-50 dark:bg-amber-950/20",
          border: "border-amber-200 dark:border-amber-900",
          text: "text-amber-900 dark:text-amber-200",
          icon: "text-amber-600 dark:text-amber-400",
          progress: "bg-amber-600",
        };
      default:
        return {
          bg: "bg-green-50 dark:bg-green-950/20",
          border: "border-green-200 dark:border-green-900",
          text: "text-green-900 dark:text-green-200",
          icon: "text-green-600 dark:text-green-400",
          progress: "bg-green-600",
        };
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case "Very High":
        return <AlertTriangle className="h-6 w-6" />;
      case "High":
        return <AlertCircle className="h-6 w-6" />;
      case "Moderate":
        return <Info className="h-6 w-6" />;
      default:
        return <CheckCircle className="h-6 w-6" />;
    }
  };

  const colors = getRiskColor(riskAssessment.riskLevel);
  const percentage = Math.round(riskAssessment.riskScore * 100);

  return (
    <div className="space-y-4">
        {/* Risk Level Badge */}
        <div
          className={`rounded-lg border p-6 ${colors.bg} ${colors.border}`}
        >
          <div className="flex items-center gap-4">
            <div className={colors.icon}>
              {getRiskIcon(riskAssessment.riskLevel)}
            </div>
            <div className="flex-1">
              <div className="mb-1 flex items-center justify-between">
                <h3 className={`text-2xl font-bold ${colors.text}`}>
                  {riskAssessment.riskLevel} Risk
                </h3>
                <span className={`text-lg font-semibold ${colors.text}`}>
                  {percentage}%
                </span>
              </div>
              <div className="mb-2 h-2 overflow-hidden rounded-full bg-white/50 dark:bg-black/20">
                <div
                  className={`h-full ${colors.progress} transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <p className={`text-sm ${colors.text}`}>
                {riskAssessment.explanation}
              </p>
            </div>
          </div>
        </div>

        {/* Risk Factors */}
        <div>
          <h4 className="mb-3 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Risk Factors Identified
          </h4>
          {riskAssessment.factors.length > 0 ? (
            <ul className="space-y-2">
              {riskAssessment.factors.map((factor, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 rounded-lg border border-[#3c4f3d]/10 bg-white p-3 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]"
                >
                  <div className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#de8246]" />
                  <span className="text-sm text-[#3c4f3d] dark:text-white/80">
                    {factor}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[#3c4f3d]/60 dark:text-white/60">
              No significant risk factors identified
            </p>
          )}
        </div>

        {/* Educational Note */}
        <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-950/20">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-blue-900 dark:text-blue-200">
            <Info className="h-4 w-4" />
            Understanding Your Risk Score
          </h4>
          <p className="text-xs leading-relaxed text-blue-900/80 dark:text-blue-200/80">
            This risk assessment is based on family history patterns and known
            genetic risk factors. A higher score indicates that genetic testing
            may provide valuable information for your healthcare. This is NOT a
            diagnosis - consult with a healthcare provider for personalized
            medical advice.
          </p>
        </div>

        {/* What This Means */}
        <div className="rounded-lg border border-[#3c4f3d]/10 bg-[#e9eeea]/50 p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]/50">
          <h4 className="mb-2 text-sm font-medium text-[#3c4f3d] dark:text-white">
            What This Means
          </h4>
          <div className="space-y-2 text-xs text-[#3c4f3d]/80 dark:text-white/70">
            {riskAssessment.riskLevel === "Very High" && (
              <>
                <p>
                  • <strong>Strongly recommended:</strong> Genetic counseling
                  and comprehensive genetic testing
                </p>
                <p>
                  • <strong>Priority:</strong> Schedule appointment as soon as
                  possible
                </p>
                <p>
                  • <strong>Coverage:</strong> Most insurance plans cover testing
                  at this risk level
                </p>
              </>
            )}
            {riskAssessment.riskLevel === "High" && (
              <>
                <p>
                  • <strong>Recommended:</strong> Genetic counseling and targeted
                  genetic testing
                </p>
                <p>
                  • <strong>Priority:</strong> Schedule within the next few months
                </p>
                <p>
                  • <strong>Coverage:</strong> Often covered by insurance
                </p>
              </>
            )}
            {riskAssessment.riskLevel === "Moderate" && (
              <>
                <p>
                  • <strong>Consider:</strong> Discussing genetic testing with
                  your healthcare provider
                </p>
                <p>
                  • <strong>Priority:</strong> Non-urgent, discuss at next
                  routine visit
                </p>
                <p>
                  • <strong>Coverage:</strong> May require pre-authorization
                </p>
              </>
            )}
            {riskAssessment.riskLevel === "Low" && (
              <>
                <p>
                  • <strong>Recommendation:</strong> Follow standard screening
                  guidelines
                </p>
                <p>
                  • <strong>Monitoring:</strong> Update if family history changes
                </p>
                <p>
                  • <strong>Prevention:</strong> Focus on lifestyle and regular
                  check-ups
                </p>
              </>
            )}
          </div>
        </div>
    </div>
  );
}
