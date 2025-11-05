import { Card } from "~/components/ui/card";
import { Brain } from "lucide-react";

export function MLModelsTab() {
  return (
    <div className="space-y-6 mt-6">
      <Card className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <Brain className="w-6 h-6 mt-1" style={{ color: "#de8246" }} />
          <h2 className="text-2xl font-semibold" style={{ color: "#3c4f3d" }}>
            Machine Learning for Variant Prediction
          </h2>
        </div>
        <p className="text-base leading-relaxed mb-4" style={{ color: "#3c4f3d" }}>
          EvoMed uses state-of-the-art machine learning models to predict the functional
          impact of genetic variants. These models analyze patterns in genomic data to
          determine whether a variant is likely to be harmless or disease-causing.
        </p>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          How ML Models Work
        </h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              1. Training Data
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Models are trained on millions of variants with known clinical outcomes from databases
              like ClinVar, COSMIC, and population studies. This includes both pathogenic
              (disease-causing) and benign (harmless) variants.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              2. Feature Learning
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              The model learns to recognize patterns associated with pathogenicity, such as:
            </p>
            <ul className="ml-6 mt-2 space-y-1 list-disc" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              <li className="text-sm">Conservation across species (evolutionarily important regions)</li>
              <li className="text-sm">Protein structure changes</li>
              <li className="text-sm">Gene function and pathway involvement</li>
              <li className="text-sm">Population allele frequencies</li>
              <li className="text-sm">Functional annotations and regulatory elements</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              3. Prediction & Scoring
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              When you input a variant, the model generates a <strong>delta score</strong> representing
              the predicted change in protein function. Higher absolute scores indicate stronger
              predicted impact (negative = likely pathogenic, positive = likely benign).
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2" style={{ color: "#3c4f3d" }}>
              4. Confidence Assessment
            </h4>
            <p className="text-sm leading-relaxed" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              The model provides a confidence score (0-100%) indicating how certain it is about
              the prediction. Higher confidence means the variant closely matches patterns in
              the training data.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          Understanding Model Outputs
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr style={{ backgroundColor: "#3c4f3d", color: "white" }}>
                <th className="p-3 text-left">Output</th>
                <th className="p-3 text-left">Description</th>
                <th className="p-3 text-left">Interpretation</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-3 font-semibold" style={{ color: "#3c4f3d" }}>Delta Score</td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Numerical value (typically -10 to +10)
                </td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Magnitude indicates impact strength; sign indicates direction
                </td>
              </tr>
              <tr className="border-b">
                <td className="p-3 font-semibold" style={{ color: "#3c4f3d" }}>Classification</td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Category (Benign, Likely Benign, VUS, etc.)
                </td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Clinical interpretation based on score thresholds
                </td>
              </tr>
              <tr className="border-b">
                <td className="p-3 font-semibold" style={{ color: "#3c4f3d" }}>Confidence</td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Percentage (0-100%)
                </td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  How certain the model is about the prediction
                </td>
              </tr>
              <tr>
                <td className="p-3 font-semibold" style={{ color: "#3c4f3d" }}>African Adjustment</td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Modified score based on African population data
                </td>
                <td className="p-3 text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                  Accounts for population-specific variant frequencies
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-3" style={{ color: "#3c4f3d" }}>
          Model Limitations & Best Practices
        </h3>
        <div className="space-y-3">
          <div className="bg-yellow-50 border-l-4 p-4" style={{ borderColor: "#eab308" }}>
            <p className="text-sm font-semibold mb-1" style={{ color: "#3c4f3d" }}>
              Important Considerations:
            </p>
            <ul className="space-y-1 ml-4 list-disc" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              <li className="text-sm">ML predictions are not diagnostic tools—always consult clinical experts</li>
              <li className="text-sm">Low confidence scores warrant further investigation</li>
              <li className="text-sm">Novel variants in understudied genes may have uncertain predictions</li>
              <li className="text-sm">Population context matters—use African adjustment for African populations</li>
              <li className="text-sm">Compare predictions with ClinVar and published literature</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
