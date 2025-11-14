import { Card } from "~/components/ui/card";
import { Info, Search, Brain, Globe, BarChart3 } from "lucide-react";

export function OverviewTab() {
  return (
    <div className="mt-6 space-y-6">
      <Card className="space-y-4 p-6">
        <div className="flex items-start gap-3">
          <div>
            <h2
              className="mb-3 text-2xl font-semibold"
              style={{ color: "#3c4f3d" }}
            >
              What is EvoMed?
            </h2>
            <p
              className="text-base leading-relaxed"
              style={{ color: "#3c4f3d" }}
            >
              EvoMed is an advanced genomic variant analysis platform
              specifically designed to provide accurate and relevant variant
              classification for African populations. By combining cutting-edge
              machine learning models with population-specific genomic data, we
              help researchers and clinicians better understand genetic
              variations and their potential health implications.
            </p>
          </div>
        </div>
      </Card>

      <Card className="space-y-4 p-6">
        <h3 className="text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Key Features
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Search className="h-5 w-5" style={{ color: "#de8246" }} />
              <h4 className="font-semibold" style={{ color: "#3c4f3d" }}>
                Gene Search & Browse
              </h4>
            </div>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "#3c4f3d", opacity: 0.8 }}
            >
              Search for specific genes or browse by chromosome using data from
              the UCSC Genome Browser.
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5" style={{ color: "#de8246" }} />
              <h4 className="font-semibold" style={{ color: "#3c4f3d" }}>
                ML-Powered Analysis
              </h4>
            </div>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "#3c4f3d", opacity: 0.8 }}
            >
              Machine learning models predict the functional impact of genetic
              variants with high accuracy.
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5" style={{ color: "#de8246" }} />
              <h4 className="font-semibold" style={{ color: "#3c4f3d" }}>
                African Population Data
              </h4>
            </div>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "#3c4f3d", opacity: 0.8 }}
            >
              Integrated African genomic data provides context-aware variant
              classification adjustments.
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" style={{ color: "#de8246" }} />
              <h4 className="font-semibold" style={{ color: "#3c4f3d" }}>
                ClinVar Integration
              </h4>
            </div>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "#3c4f3d", opacity: 0.8 }}
            >
              Compare your variants against known clinical variants from the
              ClinVar database.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-3 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Why EvoMed?
        </h3>
        <ul
          className="list-inside list-disc space-y-2"
          style={{ color: "#3c4f3d" }}
        >
          <li>
            <strong>Population-Specific Accuracy:</strong> Most genomic
            databases underrepresent African populations. EvoMed addresses this
            gap with specialized datasets.
          </li>
          <li>
            <strong>Clinical Relevance:</strong> Our ML models are trained to
            predict pathogenicity and clinical significance with high
            confidence.
          </li>
          <li>
            <strong>User-Friendly Interface:</strong> Complex genomic analysis
            made accessible through intuitive visualizations and clear
            reporting.
          </li>
          <li>
            <strong>Research-Ready:</strong> Export and compare results for
            research and clinical decision support.
          </li>
        </ul>
      </Card>
    </div>
  );
}
