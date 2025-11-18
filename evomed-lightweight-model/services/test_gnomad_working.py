"""
Test with known working variants from gnomAD
"""
import requests
import json

def test_known_variants():
    """Test with variants we know exist in gnomAD"""

    base_url = "https://gnomad.broadinstitute.org/api"

    # Test with several well-known common variants
    test_variants = [
        # Format: (variant_id, description)
        ("19-44908684-T-C", "APOE ε4 - very common Alzheimer's risk allele"),
        ("17-43094464-G-A", "BRCA1 common benign variant"),
        ("13-32315474-G-T", "BRCA2 common variant"),
        ("7-117199563-G-A", "CFTR common variant"),
        ("1-230710048-A-G", "AGT common variant"),
    ]

    query = """
    query VariantQuery($variantId: String!, $datasetId: DatasetId!) {
      variant(variantId: $variantId, dataset: $datasetId) {
        variant_id
        chrom
        pos
        ref
        alt
        genome {
          ac
          an
          af
          populations {
            id
            ac
            an
            af
          }
        }
      }
    }
    """

    for variant_id, description in test_variants:
        print("=" * 70)
        print(f"Testing: {variant_id}")
        print(f"Description: {description}")
        print("=" * 70)

        try:
            response = requests.post(
                base_url,
                json={
                    "query": query,
                    "variables": {
                        "variantId": variant_id,
                        "datasetId": "gnomad_r4"
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=15
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if "errors" in data:
                    print(f"❌ GraphQL Error: {data['errors'][0].get('message', '')}")
                elif "data" in data and data["data"].get("variant"):
                    variant = data["data"]["variant"]
                    print(f"✅ SUCCESS! Found variant")
                    print(f"   Variant ID: {variant['variant_id']}")
                    print(f"   Position: chr{variant['chrom']}:{variant['pos']}")
                    print(f"   Ref: {variant['ref']}, Alt: {variant['alt']}")

                    if variant.get("genome"):
                        genome = variant["genome"]
                        print(f"   Global AF: {genome.get('af', 'N/A')}")

                        if genome.get("populations"):
                            print("   Population Frequencies:")
                            for pop in genome["populations"]:
                                pop_id = pop.get("id")
                                pop_af = pop.get("af")
                                if pop_id and pop_af:
                                    print(f"     {pop_id}: {pop_af:.6f}")

                    # This variant works - let's use it for testing!
                    print("\n   🎉 This variant works! Can use for testing.")
                    break
                else:
                    print(f"⚠️  Variant not found in gnomAD")
            else:
                print(f"❌ HTTP Error: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Exception: {e}")

        print()

if __name__ == "__main__":
    test_known_variants()
