import { Card } from "~/components/ui/card";
import { Dna } from "lucide-react";

export function VariantAnalysisTab() {
  return (
    <div className="space-y-6 mt-6">
      <Card className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <Dna className="w-6 h-6 mt-1" style={{ color: "#de8246" }} />
          <h2 className="text-2xl font-semibold" style={{ color: "#3c4f3d" }}>
            Understanding Genetic Variants
          </h2>
        </div>
        <p className="text-base leading-relaxed mb-4" style={{ color: "#3c4f3d" }}>
          A <strong>genetic variant</strong> is a difference in DNA sequence compared to a
          reference genome. These variations occur naturally and make each person unique.
          However, some variants can affect how genes function and may be associated with
          disease risk or drug response.
        </p>
        <div className="bg-white p-4 rounded-lg border" style={{ borderColor: "#de8246" }}>
          <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>Example:</h4>
          <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
            At position 43,125,270 in the BRCA1 gene, the reference genome has an &quot;A&quot; (adenine).
            If a person has a &quot;T&quot; (thymine) at this position instead, this is a variant.
            This particular variant might affect breast cancer risk.
          </p>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          Types of Variants
        </h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
              Single Nucleotide Variants (SNVs)
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              The most common type of variant, where a single nucleotide (A, C, G, or T) is changed.
              Example: A → T
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
              Insertions and Deletions (Indels)
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Addition or removal of nucleotides in the DNA sequence. Can range from one to many base pairs.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-1" style={{ color: "#3c4f3d" }}>
              Structural Variants
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Large-scale changes affecting segments of chromosomes, including duplications, inversions,
              and translocations.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          Variant Classification
        </h3>
        <p className="text-base leading-relaxed mb-4" style={{ color: "#3c4f3d" }}>
          Variants are classified based on their predicted effect on health:
        </p>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 rounded-full mt-1.5" style={{ backgroundColor: "#22c55e" }}></div>
            <div>
              <strong style={{ color: "#3c4f3d" }}>Benign:</strong>
              <span style={{ color: "#3c4f3d", opacity: 0.8 }}> No harmful effect on health</span>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 rounded-full mt-1.5" style={{ backgroundColor: "#84cc16" }}></div>
            <div>
              <strong style={{ color: "#3c4f3d" }}>Likely Benign:</strong>
              <span style={{ color: "#3c4f3d", opacity: 0.8 }}> Probably harmless but not certain</span>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 rounded-full mt-1.5" style={{ backgroundColor: "#eab308" }}></div>
            <div>
              <strong style={{ color: "#3c4f3d" }}>Uncertain Significance (VUS):</strong>
              <span style={{ color: "#3c4f3d", opacity: 0.8 }}> Not enough evidence to classify</span>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 rounded-full mt-1.5" style={{ backgroundColor: "#f97316" }}></div>
            <div>
              <strong style={{ color: "#3c4f3d" }}>Likely Pathogenic:</strong>
              <span style={{ color: "#3c4f3d", opacity: 0.8 }}> Probably disease-causing</span>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 rounded-full mt-1.5" style={{ backgroundColor: "#ef4444" }}></div>
            <div>
              <strong style={{ color: "#3c4f3d" }}>Pathogenic:</strong>
              <span style={{ color: "#3c4f3d", opacity: 0.8 }}> Known to cause disease</span>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          How to Analyze Variants in EvoMed
        </h3>
        <ol className="space-y-2 list-decimal list-inside" style={{ color: "#3c4f3d" }}>
          <li>Search for or browse to a gene of interest (e.g., BRCA1, TP53)</li>
          <li>View the gene sequence and known variants from ClinVar</li>
          <li>Input your variant details: position, reference nucleotide, alternative nucleotide</li>
          <li>Toggle African population adjustment (recommended for African populations)</li>
          <li>Click &quot;Analyze Variant&quot; to get ML-powered predictions</li>
          <li>Review the delta score, classification, and confidence level</li>
          <li>Compare with known variants or export results</li>
        </ol>
      </Card>
    </div>
  );
}
