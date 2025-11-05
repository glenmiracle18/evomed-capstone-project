"use client";

import { Card } from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { OverviewTab } from "~/components/docs/overview-tab";
import { VariantAnalysisTab } from "~/components/docs/variant-analysis-tab";
import { MLModelsTab } from "~/components/docs/ml-models-tab";
import { AfricanGenomicsTab } from "~/components/docs/african-genomics-tab";
import { GettingStartedTab } from "~/components/docs/getting-started-tab";

export default function DocsPage() {
  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: "#e9eeea" }}>
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold" style={{ color: "#3c4f3d" }}>
            EvoMed Documentation
          </h1>
          <p className="text-lg" style={{ color: "#3c4f3d", opacity: 0.8 }}>
            Understanding Variant Analysis and Machine Learning
          </p>
        </div>

        {/* Tabs Navigation */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="variant-analysis">Variant Analysis</TabsTrigger>
            <TabsTrigger value="ml-models">ML Models</TabsTrigger>
            <TabsTrigger value="african-genomics">African Genomics</TabsTrigger>
            <TabsTrigger value="getting-started">Getting Started</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <OverviewTab />
          </TabsContent>

          <TabsContent value="variant-analysis">
            <VariantAnalysisTab />
          </TabsContent>

          <TabsContent value="ml-models">
            <MLModelsTab />
          </TabsContent>

          <TabsContent value="african-genomics">
            <AfricanGenomicsTab />
          </TabsContent>

          <TabsContent value="getting-started">
            <GettingStartedTab />
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <Card className="mt-8 p-6">
          <div className="space-y-2 text-center">
            <p className="text-sm font-semibold" style={{ color: "#3c4f3d" }}>
              EvoMed - African Variant Analysis ML Model
            </p>
            <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Advancing genomic medicine for African populations through machine
              learning and population-specific data integration.
            </p>
            <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.6 }}>
              For research and educational purposes. Not for clinical diagnosis.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
