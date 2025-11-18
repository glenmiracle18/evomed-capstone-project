"use client";

import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import {
  Clipboard,
  DollarSign,
  MapPin,
  CheckCircle2,
  FileText,
} from "lucide-react";
import { Button } from "~/components/ui/button";

interface TestingRecommendationsProps {
  testingStrategy: string;
  estimatedCost: string;
  nextSteps: string[];
  riskLevel: string;
}

export function TestingRecommendations({
  testingStrategy,
  estimatedCost,
  nextSteps,
  riskLevel,
}: TestingRecommendationsProps) {
  const getStrategyInfo = (strategy: string) => {
    switch (strategy) {
      case "comprehensive_panel":
        return {
          title: "Comprehensive Multi-Gene Panel",
          description:
            "Test multiple cancer susceptibility genes simultaneously. Most thorough option for high-risk individuals.",
          includes: [
            "BRCA1 and BRCA2 (full sequencing)",
            "PALB2, CHEK2, ATM, TP53",
            "Additional cancer genes (10-30 genes)",
            "Copy number variant analysis",
            "Detailed genetic counseling",
          ],
        };
      case "targeted_panel":
        return {
          title: "Targeted BRCA1/2 Panel",
          description:
            "Focus on the most common cancer genes. Cost-effective for moderate-risk individuals.",
          includes: [
            "BRCA1 and BRCA2 sequencing",
            "Common pathogenic variants",
            "Population-specific founder mutations",
            "Basic genetic counseling",
          ],
        };
      default:
        return {
          title: "Standard Screening Approach",
          description:
            "Follow general population guidelines. Genetic testing not immediately necessary.",
          includes: [
            "Regular health screenings per age",
            "Mammography as recommended",
            "Clinical breast exams",
            "Lifestyle risk reduction",
            "Monitor family history changes",
          ],
        };
    }
  };

  const strategyInfo = getStrategyInfo(testingStrategy);

  const generatePDF = () => {
    // In a real implementation, this would generate a proper PDF
    const report = `
GENETIC TESTING RECOMMENDATIONS
================================
Generated: ${new Date().toLocaleDateString()}

RISK LEVEL: ${riskLevel}

RECOMMENDED TESTING STRATEGY
${strategyInfo.title}
${strategyInfo.description}

ESTIMATED COST: ${estimatedCost}

WHAT'S INCLUDED:
${strategyInfo.includes.map((item, i) => `${i + 1}. ${item}`).join('\n')}

NEXT STEPS:
${nextSteps.map((step, i) => `${i + 1}. ${step}`).join('\n')}

IMPORTANT NOTES:
- This is not a medical diagnosis
- Consult with a healthcare provider before proceeding
- Costs may vary by provider and insurance coverage
- Genetic counseling is recommended before and after testing
- Test results should be interpreted by qualified professionals

For questions, contact your healthcare provider or a genetic counselor.
    `.trim();

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `testing-recommendations-${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-[#3c4f3d] dark:text-white">
              <Clipboard className="h-5 w-5" />
              Testing Recommendations
            </CardTitle>
            <p className="mt-1 text-sm text-[#3c4f3d]/60 dark:text-white/60">
              Personalized guidance based on your risk assessment
            </p>
          </div>
          <Button
            onClick={generatePDF}
            variant="outline"
            size="sm"
            className="border-[#3c4f3d]/20 hover:border-[#de8246] hover:bg-[#de8246]/5 hover:text-[#de8246]"
          >
            <FileText className="mr-2 h-4 w-4" />
            Download Summary
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Recommended Strategy */}
        <div className="rounded-lg border border-[#de8246]/20 bg-[#de8246]/5 p-4 dark:bg-[#de8246]/10">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-semibold text-[#3c4f3d] dark:text-white">
              {strategyInfo.title}
            </h3>
            <Badge className="bg-[#de8246] text-white">Recommended</Badge>
          </div>
          <p className="mb-3 text-sm text-[#3c4f3d]/80 dark:text-white/80">
            {strategyInfo.description}
          </p>
          <div className="rounded-lg bg-white p-3 dark:bg-[#1a1f1a]">
            <h4 className="mb-2 text-xs font-medium text-[#3c4f3d]/70 dark:text-white/70">
              What's Included:
            </h4>
            <ul className="space-y-1">
              {strategyInfo.includes.map((item, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-[#3c4f3d] dark:text-white"
                >
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Cost Estimate */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
            <div className="mb-1 flex items-center gap-2 text-[#3c4f3d]/60 dark:text-white/60">
              <DollarSign className="h-4 w-4" />
              <span className="text-xs font-medium">Estimated Cost</span>
            </div>
            <div className="text-2xl font-bold text-[#de8246]">
              {estimatedCost}
            </div>
            <p className="mt-1 text-xs text-[#3c4f3d]/60 dark:text-white/60">
              Without insurance
            </p>
          </div>
          <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
            <div className="mb-1 flex items-center gap-2 text-[#3c4f3d]/60 dark:text-white/60">
              <DollarSign className="h-4 w-4" />
              <span className="text-xs font-medium">With Insurance</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              $0-{estimatedCost.split('-')[0]}
            </div>
            <p className="mt-1 text-xs text-[#3c4f3d]/60 dark:text-white/60">
              {riskLevel === "Very High" || riskLevel === "High"
                ? "Often fully covered"
                : "May require pre-auth"}
            </p>
          </div>
        </div>

        {/* Next Steps */}
        <div>
          <h4 className="mb-3 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Your Next Steps
          </h4>
          <div className="space-y-2">
            {nextSteps.map((step, index) => (
              <div
                key={index}
                className="flex items-start gap-3 rounded-lg border border-[#3c4f3d]/10 bg-white p-3 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]"
              >
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#de8246] text-xs font-bold text-white">
                  {index + 1}
                </div>
                <p className="text-sm text-[#3c4f3d] dark:text-white">{step}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Where to Get Tested */}
        <div className="rounded-lg border border-[#3c4f3d]/10 bg-[#e9eeea]/50 p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]/50">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-[#3c4f3d] dark:text-white">
            <MapPin className="h-4 w-4" />
            Where to Get Tested
          </h4>
          <div className="space-y-2 text-sm text-[#3c4f3d]/80 dark:text-white/70">
            <p>
              <strong>Local Options:</strong>
            </p>
            <ul className="ml-4 list-disc space-y-1 text-xs">
              <li>Regional hospitals with genetic counseling services</li>
              <li>Community health centers (subsidized rates available)</li>
              <li>University medical centers (research programs)</li>
              <li>Mobile health clinics (for rural areas)</li>
            </ul>
            <p className="mt-3">
              <strong>Affordable Testing Programs:</strong>
            </p>
            <ul className="ml-4 list-disc space-y-1 text-xs">
              <li>
                <strong>Direct-to-consumer testing:</strong> Color Genomics,
                Invitae (~$250)
              </li>
              <li>
                <strong>Research studies:</strong> Free testing for eligible
                participants
              </li>
              <li>
                <strong>Non-profit programs:</strong> FORCE, Bright Pink (financial
                assistance)
              </li>
            </ul>
          </div>
        </div>

        {/* Important Disclaimers */}
        <div className="rounded-lg bg-amber-50 p-4 dark:bg-amber-950/20">
          <h4 className="mb-2 text-sm font-medium text-amber-900 dark:text-amber-200">
            Important Information
          </h4>
          <ul className="space-y-1 text-xs text-amber-900/80 dark:text-amber-200/80">
            <li>
              • This is <strong>not a medical diagnosis</strong> - consult with
              healthcare providers
            </li>
            <li>
              • Genetic counseling is <strong>strongly recommended</strong> before
              and after testing
            </li>
            <li>
              • Test results should be interpreted by{" "}
              <strong>qualified professionals</strong>
            </li>
            <li>
              • Insurance coverage varies - check with your provider before
              testing
            </li>
            <li>
              • Consider privacy implications of genetic testing before proceeding
            </li>
          </ul>
        </div>

        {/* Support Resources */}
        <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
          <h4 className="mb-2 text-sm font-medium text-[#3c4f3d] dark:text-white">
            Support Resources
          </h4>
          <div className="space-y-2 text-xs text-[#3c4f3d]/80 dark:text-white/70">
            <p>
              <strong>Find a Genetic Counselor:</strong> nsgc.org/findagc
            </p>
            <p>
              <strong>BRCA Support:</strong> facingourrisk.org
            </p>
            <p>
              <strong>Financial Assistance:</strong> pancan.org/facing-pancreatic-cancer/patient-services/financial-resources/
            </p>
            <p>
              <strong>African-Focused Resources:</strong> Sisters Network Inc,
              The Black Women's Health Imperative
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
