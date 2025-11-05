import { Card } from "~/components/ui/card";

export function GettingStartedTab() {
  return (
    <div className="mt-6 space-y-6">
      <Card className="p-6">
        <h2
          className="mb-4 text-2xl font-semibold"
          style={{ color: "#3c4f3d" }}
        >
          Getting Started with EvoMed
        </h2>
        <p
          className="mb-6 text-base leading-relaxed"
          style={{ color: "#3c4f3d" }}
        >
          Follow this step-by-step guide to start analyzing genetic variants
          with EvoMed.
        </p>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Step 1: Search for a Gene
        </h3>
        <div className="space-y-3">
          <p
            className="text-sm leading-relaxed"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            From the main dashboard, you can search for genes in two ways:
          </p>
          <ul
            className="ml-6 list-disc space-y-2"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            <li className="text-sm">
              <strong>Search by Gene Symbol:</strong> Enter a gene symbol (e.g.,
              BRCA1, TP53, APOE) or gene name in the search box
            </li>
            <li className="text-sm">
              <strong>Browse by Chromosome:</strong> Select a chromosome
              (chr1-chr22, chrX, chrY) to view all genes on that chromosome
            </li>
          </ul>
          <div
            className="mt-3 rounded border bg-white p-4"
            style={{ borderColor: "#de8246" }}
          >
            <p
              className="mb-1 text-sm font-semibold"
              style={{ color: "#3c4f3d" }}
            >
              Try it:
            </p>
            <p className="text-sm" style={{ color: "#3c4f3d", opacity: 0.8 }}>
              Search for &quot;BRCA1&quot; (breast cancer gene) or
              &quot;TP53&quot; (tumor suppressor gene) to see example results.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Step 2: View Gene Details
        </h3>
        <div className="space-y-3">
          <p
            className="text-sm leading-relaxed"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            Click on any gene from the search results to view its detailed page,
            which includes:
          </p>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Gene Information
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                Chromosomal location, strand direction, and gene summary
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Gene Sequence
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                Interactive nucleotide sequence viewer with color-coded bases
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Known Variants
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                ClinVar variants with clinical significance and annotations
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Variant Analysis
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                Tool to analyze custom variants with ML predictions
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Step 3: Analyze a Variant
        </h3>
        <div className="space-y-3">
          <p
            className="mb-3 text-sm leading-relaxed"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            To analyze a custom variant:
          </p>
          <ol
            className="list-inside list-decimal space-y-2"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            <li className="text-sm">
              In the <strong>Variant Analysis</strong> section, enter the
              genomic position (must be within the gene&apos;s range)
            </li>
            <li className="text-sm">
              Select the <strong>reference nucleotide</strong> (what appears in
              the reference genome: A, C, G, or T)
            </li>
            <li className="text-sm">
              Select the <strong>alternative nucleotide</strong> (the variant
              you&apos;re testing)
            </li>
            <li className="text-sm">
              Toggle <strong>African Population Adjustment</strong> if analyzing
              African ancestry samples
            </li>
            <li className="text-sm">
              Click <strong>&quot;Analyze Variant&quot;</strong> and wait for
              the ML model to generate predictions
            </li>
          </ol>
          <div
            className="mt-4 rounded border-l-4 bg-green-50 p-4"
            style={{ borderColor: "#22c55e" }}
          >
            <p
              className="mb-1 text-sm font-semibold"
              style={{ color: "#3c4f3d" }}
            >
              Example Analysis:
            </p>
            <ul
              className="space-y-1 text-xs"
              style={{ color: "#3c4f3d", opacity: 0.8 }}
            >
              <li>Gene: BRCA1</li>
              <li>Position: 43125270</li>
              <li>Reference: A</li>
              <li>Alternative: T</li>
              <li>
                Result: Delta score, classification, confidence, and optional
                African adjustment
              </li>
            </ul>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Step 4: Interpret Results
        </h3>
        <div className="space-y-3">
          <p
            className="text-sm leading-relaxed"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            After analysis, review the following information:
          </p>
          <div className="space-y-3">
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Delta Score
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                The numerical prediction of functional impact. Larger absolute
                values indicate stronger predicted effects.
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Classification
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                Clinical category (Benign, Likely Benign, VUS, Likely
                Pathogenic, Pathogenic) with color coding.
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Confidence
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                How confident the model is (0-100%). Higher confidence = more
                reliable prediction.
              </p>
            </div>
            <div className="rounded border bg-white p-3">
              <h4
                className="mb-1 text-sm font-semibold"
                style={{ color: "#3c4f3d" }}
              >
                Population Context
              </h4>
              <p className="text-xs" style={{ color: "#3c4f3d", opacity: 0.8 }}>
                If African adjustment is enabled, see population frequency and
                adjusted score.
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 text-xl font-semibold" style={{ color: "#3c4f3d" }}>
          Step 5: Compare & Export
        </h3>
        <div className="space-y-2">
          <p
            className="text-sm leading-relaxed"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            After analyzing your variant:
          </p>
          <ul
            className="ml-6 list-disc space-y-2"
            style={{ color: "#3c4f3d", opacity: 0.8 }}
          >
            <li className="text-sm">
              Compare your results with <strong>known variants</strong> from
              ClinVar shown in the Known Variants section
            </li>
            <li className="text-sm">
              Use the <strong>comparison modal</strong> to view side-by-side
              analysis of multiple variants
            </li>
            <li className="text-sm">
              Review the <strong>gene sequence</strong> to understand the
              genomic context around your variant
            </li>
            <li className="text-sm">
              Document your findings for clinical or research use (export
              features coming soon)
            </li>
          </ul>
        </div>
      </Card>

      <Card className="bg-yellow-50 p-6">
        <h3 className="mb-2 text-lg font-semibold" style={{ color: "#3c4f3d" }}>
          Need Help?
        </h3>
        <p
          className="mb-3 text-sm leading-relaxed"
          style={{ color: "#3c4f3d", opacity: 0.8 }}
        >
          If you encounter issues or have questions about using EvoMed:
        </p>
        <ul
          className="ml-6 list-disc space-y-1"
          style={{ color: "#3c4f3d", opacity: 0.8 }}
        >
          <li className="text-sm">
            Review the documentation tabs above for detailed explanations
          </li>
          <li className="text-sm">
            Check that variant positions are within the gene&apos;s genomic
            range
          </li>
          <li className="text-sm">
            Ensure reference nucleotides match the gene sequence at that
            position
          </li>
          <li className="text-sm">
            Contact our support team for technical assistance
          </li>
        </ul>
      </Card>
    </div>
  );
}
