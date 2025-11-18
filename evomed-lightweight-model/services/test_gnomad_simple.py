"""
Test with simplified query to find correct schema
"""
import requests
import json

def test_simple_query():
    """Test with minimal query to understand schema"""

    base_url = "https://gnomad.broadinstitute.org/api"
    variant_id = "19-44908684-T-C"  # APOE ε4, definitely exists

    # Simplified query - just basic fields
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
          populations {
            id
            ac
            an
          }
        }
      }
    }
    """

    print("=" * 70)
    print(f"Testing variant: {variant_id} (APOE ε4)")
    print("With simplified query (ac/an only, no af)")
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

        print(f"Status: {response.status_code}\n")

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print(f"❌ GraphQL Error:")
                for error in data["errors"]:
                    print(f"   {error.get('message', '')}")
            elif "data" in data and data["data"].get("variant"):
                variant = data["data"]["variant"]
                print(f"✅ SUCCESS! Found variant\n")
                print(f"Variant ID: {variant['variant_id']}")
                print(f"Position: chr{variant['chrom']}:{variant['pos']}")
                print(f"Ref: {variant['ref']}, Alt: {variant['alt']}")

                if variant.get("genome"):
                    genome = variant["genome"]
                    global_ac = genome.get('ac', 0)
                    global_an = genome.get('an', 0)
                    global_af = global_ac / global_an if global_an > 0 else 0

                    print(f"\nGlobal:")
                    print(f"  AC: {global_ac}, AN: {global_an}")
                    print(f"  AF (calculated): {global_af:.6f}")

                    if genome.get("populations"):
                        print(f"\nPopulation Frequencies:")
                        for pop in genome["populations"]:
                            pop_id = pop.get("id")
                            pop_ac = pop.get("ac", 0)
                            pop_an = pop.get("an", 0)
                            pop_af = pop_ac / pop_an if pop_an > 0 else 0

                            if pop_id == "afr":  # African population
                                print(f"  {pop_id.upper()}: AC={pop_ac}, AN={pop_an}, AF={pop_af:.6f} ⭐")
                            elif pop_id in ["eas", "nfe", "sas", "amr"]:
                                print(f"  {pop_id.upper()}: AC={pop_ac}, AN={pop_an}, AF={pop_af:.6f}")

                print("\n✅ Query works! Need to calculate AF from AC/AN")
                return True
            else:
                print(f"⚠️  Variant not found in gnomAD")
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

    return False

if __name__ == "__main__":
    test_simple_query()
