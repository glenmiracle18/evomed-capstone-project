import { Card } from "~/components/ui/card";
import { Globe } from "lucide-react";

export function AfricanGenomicsTab() {
  return (
    <div className="space-y-6 mt-6">
      <Card className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <Globe className="w-6 h-6 mt-1" style={{ color: "#de8246" }} />
          <h2 className="text-2xl font-semibold" style={{ color: "#3c4f3d" }}>
            African Genomics & Population-Specific Analysis
          </h2>
        </div>
        <p className="text-base leading-relaxed mb-4" style={{ color: "#3c4f3d" }}>
          One of EvoMed&apos;s key innovations is the integration of African population-specific
          genomic data. This addresses a critical gap in genomic medicine: most genetic
          databases and prediction models are heavily biased toward European populations.
        </p>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          Why African Genomics Matters
        </h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              Genetic Diversity
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              African populations harbor the highest genetic diversity of any human population.
              This means many variants found in African individuals are rare or absent in other populations,
              making them more likely to be misclassified as pathogenic when they&apos;re actually benign.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              Database Representation Gap
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Less than 2% of genome-wide association studies include African populations.
              This underrepresentation means that variant classification models trained on these
              databases may be inaccurate for African individuals.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              Clinical Impact
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Misclassification of variants can lead to incorrect disease risk assessments,
              inappropriate treatment decisions, and reduced effectiveness of precision medicine
              approaches for African populations.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          How African Adjustment Works
        </h3>
        <div className="space-y-4">
          <p className="text-base leading-relaxed" style={{ color: "#3c4f3d" }}>
            When you enable &quot;African Population Adjustment&quot; in the variant analysis tool,
            EvoMed applies the following modifications:
          </p>
          <div className="space-y-3">
            <div className="flex gap-3">
              <div className="text-2xl" style={{ color: "#de8246" }}>1</div>
              <div>
                <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
                  Population Allele Frequency Check
                </h4>
                <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Queries African-specific databases (e.g., AfricanGenome.org, H3Africa) to
                  determine how common the variant is in African populations.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="text-2xl" style={{ color: "#de8246" }}>2</div>
              <div>
                <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
                  Score Recalibration
                </h4>
                <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  If the variant is common in African populations (&gt;1% frequency) but rare globally,
                  the pathogenicity score is adjusted toward benign, as common variants are
                  unlikely to be disease-causing.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="text-2xl" style={{ color: "#de8246" }}>3</div>
              <div>
                <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
                  Population Context Display
                </h4>
                <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Results show both the original and adjusted scores, along with population
                  frequency data, so you can understand how the adjustment affects the classification.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          When to Use African Adjustment
        </h3>
        <div className="space-y-3">
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "#de8246" }}></div>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d" }}>
              <strong>Recommended:</strong> When analyzing variants from individuals of African ancestry
            </p>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "#de8246" }}></div>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d" }}>
              <strong>Recommended:</strong> For research studies focused on African populations
            </p>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "#de8246" }}></div>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d" }}>
              <strong>Consider:</strong> When standard predictions show high pathogenicity but the
              variant has no known disease association
            </p>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "#de8246" }}></div>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d" }}>
              <strong>Not Needed:</strong> For variants already well-characterized in ClinVar across
              multiple populations
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6 bg-blue-50">
        <h3 className="text-lg font-semibold mb-2" style={{ color: "#3c4f3d" }}>
          Contributing to African Genomics
        </h3>
        <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
          EvoMed is committed to expanding African genomic representation. If you&apos;re conducting
          research with African populations and would like to contribute data or collaborate,
          please contact our research team. Together, we can improve genomic medicine for all populations.
        </p>
      </Card>
    </div>
  );
}
