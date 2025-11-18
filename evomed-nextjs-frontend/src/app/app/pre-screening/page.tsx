"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { Card, CardContent } from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import {
  DemographicsForm,
  type DemographicsData,
} from "~/components/demographics-form";
import {
  FamilyHistoryQuestionnaire,
  type FamilyMember,
} from "~/components/family-history-questionnaire";
import { RiskAssessmentDisplay } from "~/components/risk-assessment-display";
import { VariantRecommendationsPanel } from "~/components/variant-recommendations-panel";
import { TestingRecommendations } from "~/components/testing-recommendations";
import {
  ArrowRight,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Users,
  User,
  FlaskConical,
  Stethoscope,
} from "lucide-react";

type Step = "intro" | "demographics" | "family-history" | "results";

interface RecommendationResponse {
  riskAssessment: {
    riskScore: number;
    riskLevel: "Low" | "Moderate" | "High" | "Very High";
    explanation: string;
    factors: string[];
  };
  recommendedGenes: string[];
  priorityVariants: Array<{
    gene: string;
    variant: string;
    hgvsNotation: string;
    populationFrequency: number;
    pathogenicity: string;
    clinicalSignificance: string;
    cancerRisk: string;
    gnomadId?: string;
  }>;
  testingStrategy: string;
  estimatedCost: string;
  nextSteps: string[];
  ancestry: string;
}

export default function PreScreeningPage() {
  const [currentStep, setCurrentStep] = useState<Step>("intro");
  const [demographics, setDemographics] = useState<DemographicsData>({
    age: 0,
    sex: "",
    ancestry: "",
    personalHistory: { hasCancer: false },
  });
  const [familyHistory, setFamilyHistory] = useState<FamilyMember[]>([]);
  const [recommendations, setRecommendations] =
    useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canProceedFromDemographics = () => {
    return (
      demographics.age > 0 &&
      demographics.sex !== "" &&
      demographics.ancestry !== ""
    );
  };

  const canProceedFromFamilyHistory = () => {
    // User can proceed even with no family history
    return true;
  };

  const handleGetRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/recommend-variants", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ancestry: demographics.ancestry,
          familyHistory: familyHistory,
          age: demographics.age,
          sex: demographics.sex,
          personalHistory: demographics.personalHistory,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get recommendations");
      }

      const data = await response.json();
      setRecommendations(data);
      setCurrentStep("results");
    } catch (err) {
      setError(
        "Failed to generate recommendations. Please try again."
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepIndicator = () => {
    const steps = [
      { id: "intro", label: "Welcome", icon: CheckCircle },
      { id: "demographics", label: "Your Info", icon: User },
      { id: "family-history", label: "Family History", icon: Users },
      { id: "results", label: "Results", icon: FlaskConical },
    ];

    const currentIndex = steps.findIndex((s) => s.id === currentStep);

    return (
      <div className="mb-8 flex items-center justify-center gap-2">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isUpcoming = index > currentIndex;

          return (
            <div key={step.id} className="flex items-center">
              <div
                className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
                  isCurrent
                    ? "bg-[#de8246] text-white"
                    : isCompleted
                      ? "bg-green-100 text-green-700 dark:bg-green-950/30 dark:text-green-400"
                      : "bg-[#e9eeea] text-[#3c4f3d]/40 dark:bg-[#1a1f1a] dark:text-white/40"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="text-sm font-medium">{step.label}</span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`mx-2 h-0.5 w-8 ${
                    isCompleted
                      ? "bg-green-500"
                      : "bg-[#3c4f3d]/10 dark:bg-white/10"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#e9eeea] p-6 dark:bg-[#1a1f1a]">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-6 text-center">
          <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-[#de8246]/10 px-4 py-1.5">
            <Stethoscope className="h-4 w-4 text-[#de8246]" />
            <span className="text-sm font-medium text-[#de8246]">
              Pre-Screening Tool
            </span>
          </div>
          <h1 className="mb-2 text-3xl font-bold text-[#3c4f3d] dark:text-white">
            Genetic Testing Recommender
          </h1>
          <p className="text-[#3c4f3d]/60 dark:text-white/60">
            Find out which genetic tests are most relevant for you
          </p>
        </div>

        {/* Step Indicator */}
        {renderStepIndicator()}

        {/* Content */}
        <div className="space-y-6">
          {/* Intro Step */}
          {currentStep === "intro" && (
            <Card className="border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 dark:bg-[#242924]">
              <CardContent className="p-8">
                <div className="mb-6 text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[#de8246]/10">
                    <Stethoscope className="h-8 w-8 text-[#de8246]" />
                  </div>
                  <h2 className="mb-2 text-2xl font-bold text-[#3c4f3d] dark:text-white">
                    Welcome to the Genetic Pre-Screening Tool
                  </h2>
                  <p className="text-[#3c4f3d]/60 dark:text-white/60">
                    Designed specifically for underserved and rural populations
                  </p>
                </div>

                <div className="mb-6 space-y-4">
                  <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-950/20">
                    <h3 className="mb-2 font-semibold text-blue-900 dark:text-blue-200">
                      The Problem We're Solving
                    </h3>
                    <p className="text-sm text-blue-900/80 dark:text-blue-200/80">
                      Traditional genetic testing costs $1,000+ and requires
                      knowing your exact genetic sequence. This creates a barrier
                      for rural communities and underserved populations.
                    </p>
                  </div>

                  <div className="rounded-lg bg-green-50 p-4 dark:bg-green-950/20">
                    <h3 className="mb-2 font-semibold text-green-900 dark:text-green-200">
                      Our Solution
                    </h3>
                    <p className="text-sm text-green-900/80 dark:text-green-200/80">
                      Based on your family history and ancestry, we'll recommend
                      specific variants to test - reducing costs by{" "}
                      <strong>20x</strong> (as low as $50-100) while maintaining
                      accuracy for your population.
                    </p>
                  </div>

                  <div className="rounded-lg border border-[#3c4f3d]/10 bg-white p-4 dark:border-[#3c4f3d]/20 dark:bg-[#1a1f1a]">
                    <h3 className="mb-3 font-semibold text-[#3c4f3d] dark:text-white">
                      What You'll Get
                    </h3>
                    <ul className="space-y-2 text-sm text-[#3c4f3d]/80 dark:text-white/70">
                      <li className="flex items-start gap-2">
                        <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                        <span>
                          Personalized risk assessment based on family history
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                        <span>
                          List of 20 most common genetic variants in your
                          population
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                        <span>
                          Targeted testing recommendations (20x cheaper than
                          full genome)
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                        <span>
                          Downloadable report to share with healthcare providers
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                        <span>
                          Next steps and resources for affordable testing
                        </span>
                      </li>
                    </ul>
                  </div>

                  <div className="rounded-lg bg-amber-50 p-4 dark:bg-amber-950/20">
                    <h3 className="mb-2 font-semibold text-amber-900 dark:text-amber-200">
                      Privacy & Security
                    </h3>
                    <p className="text-sm text-amber-900/80 dark:text-amber-200/80">
                      All data is processed locally. We don't store or share your
                      information. This tool provides recommendations only - it's
                      not a medical diagnosis.
                    </p>
                  </div>
                </div>

                <div className="flex justify-center">
                  <Button
                    onClick={() => setCurrentStep("demographics")}
                    className="bg-[#de8246] px-8 hover:bg-[#de8246]/90"
                    size="lg"
                  >
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Demographics Step */}
          {currentStep === "demographics" && (
            <>
              <DemographicsForm
                onUpdate={setDemographics}
                initialData={demographics}
              />
              <div className="flex justify-between">
                <Button
                  onClick={() => setCurrentStep("intro")}
                  variant="outline"
                  className="border-[#3c4f3d]/20"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back
                </Button>
                <Button
                  onClick={() => setCurrentStep("family-history")}
                  disabled={!canProceedFromDemographics()}
                  className="bg-[#de8246] hover:bg-[#de8246]/90"
                >
                  Next: Family History
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </>
          )}

          {/* Family History Step */}
          {currentStep === "family-history" && (
            <>
              <FamilyHistoryQuestionnaire
                onUpdate={setFamilyHistory}
                initialData={familyHistory}
              />
              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/20 dark:text-red-200">
                  {error}
                </div>
              )}
              <div className="flex justify-between">
                <Button
                  onClick={() => setCurrentStep("demographics")}
                  variant="outline"
                  className="border-[#3c4f3d]/20"
                  disabled={isLoading}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back
                </Button>
                <Button
                  onClick={handleGetRecommendations}
                  disabled={!canProceedFromFamilyHistory() || isLoading}
                  className="bg-[#de8246] hover:bg-[#de8246]/90"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Get Recommendations
                      <FlaskConical className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
            </>
          )}

          {/* Results Step */}
          {currentStep === "results" && recommendations && (
            <>
              <div className="space-y-6">
                {/* Success Message */}
                <Card className="border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/20">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                      <div>
                        <h3 className="font-semibold text-green-900 dark:text-green-200">
                          Analysis Complete!
                        </h3>
                        <p className="text-sm text-green-900/80 dark:text-green-200/80">
                          Your personalized recommendations are ready. Scroll
                          down to view all results.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Tabbed Results */}
                <Tabs defaultValue="risk" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 bg-white dark:bg-[#242924] border border-[#3c4f3d]/10 dark:border-[#3c4f3d]/20 rounded-lg p-1">
                    <TabsTrigger
                      value="risk"
                      className="rounded-md data-[state=active]:bg-[#de8246] data-[state=active]:text-white"
                    >
                      Risk Assessment
                    </TabsTrigger>
                    <TabsTrigger
                      value="variants"
                      className="rounded-md data-[state=active]:bg-[#de8246] data-[state=active]:text-white"
                    >
                      Recommended Variants
                    </TabsTrigger>
                    <TabsTrigger
                      value="next-steps"
                      className="rounded-md data-[state=active]:bg-[#de8246] data-[state=active]:text-white"
                    >
                      Next Steps
                    </TabsTrigger>
                  </TabsList>
                  <TabsContent value="risk" className="mt-4">
                    <RiskAssessmentDisplay
                      riskAssessment={recommendations.riskAssessment}
                    />
                  </TabsContent>
                  <TabsContent value="variants" className="mt-4">
                    <VariantRecommendationsPanel
                      variants={recommendations.priorityVariants}
                      ancestry={recommendations.ancestry}
                      recommendedGenes={recommendations.recommendedGenes}
                    />
                  </TabsContent>
                  <TabsContent value="next-steps" className="mt-4">
                    <TestingRecommendations
                      testingStrategy={recommendations.testingStrategy}
                      estimatedCost={recommendations.estimatedCost}
                      nextSteps={recommendations.nextSteps}
                      riskLevel={recommendations.riskAssessment.riskLevel}
                    />
                  </TabsContent>
                </Tabs>
              </div>

              <div className="flex justify-between">
                <Button
                  onClick={() => {
                    setCurrentStep("intro");
                    setRecommendations(null);
                    setFamilyHistory([]);
                  }}
                  variant="outline"
                  className="border-[#3c4f3d]/20"
                >
                  Start Over
                </Button>
                <Button
                  onClick={() => window.print()}
                  className="bg-[#3c4f3d] hover:bg-[#3c4f3d]/90"
                >
                  Print Results
                </Button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-[#3c4f3d]/50 dark:text-white/50">
          <p>
            This tool is for educational and informational purposes only. It
            does not provide medical advice.
          </p>
          <p className="mt-1">
            Always consult with qualified healthcare professionals for medical
            decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
