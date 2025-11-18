"""
gnomAD API integration for African population frequency data
"""

import requests
from typing import Optional, Dict
import time


class GnomADAPI:
    """Fetch population frequency data from gnomAD"""

    def __init__(self, cache_enabled: bool = True):
        self.graphql_url = "https://gnomad.broadinstitute.org/api"
        self.cache_enabled = cache_enabled
        self.cache = {}

    def get_variant_frequency(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        dataset: str = "gnomad_r4"  # gnomAD v4 (latest)
    ) -> Optional[Dict]:
        """
        Get population frequencies for a variant from gnomAD

        Args:
            chromosome: Chromosome (e.g., "17" or "chr17")
            position: Variant position (1-based)
            ref: Reference allele
            alt: Alternate allele
            dataset: gnomAD dataset version

        Returns:
            Dictionary with population frequencies, or None if not found
        """
        # Normalize chromosome
        chrom = chromosome.replace("chr", "")

        # Create variant ID
        variant_id = f"{chrom}-{position}-{ref}-{alt}"

        # Check cache
        if self.cache_enabled and variant_id in self.cache:
            return self.cache[variant_id]

        # GraphQL query for gnomAD
        query = """
        query VariantFrequency($variantId: String!, $datasetId: DatasetId!) {
          variant(variantId: $variantId, dataset: $datasetId) {
            variant_id
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

        variables = {
            "variantId": variant_id,
            "datasetId": dataset
        }

        try:
            response = requests.post(
                self.graphql_url,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Parse response
            if "data" in data and data["data"]["variant"]:
                variant_data = data["data"]["variant"]
                genome_data = variant_data.get("genome", {})

                # Extract population frequencies
                populations = genome_data.get("populations", [])

                # Build result dictionary
                result = {
                    "variant_id": variant_id,
                    "global_af": genome_data.get("af"),
                    "global_ac": genome_data.get("ac"),
                    "global_an": genome_data.get("an"),
                    "populations": {}
                }

                # Extract specific population frequencies
                for pop in populations:
                    pop_id = pop.get("id")
                    if pop_id:
                        result["populations"][pop_id] = {
                            "af": pop.get("af"),
                            "ac": pop.get("ac"),
                            "an": pop.get("an")
                        }

                # Cache the result
                if self.cache_enabled:
                    self.cache[variant_id] = result

                return result
            else:
                # Variant not found in gnomAD
                return None

        except requests.exceptions.RequestException as e:
            print(f"⚠️  gnomAD API error for {variant_id}: {e}")
            return None

    def get_african_frequency(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str
    ) -> Optional[float]:
        """
        Get African/African American population frequency specifically

        Args:
            chromosome: Chromosome
            position: Variant position
            ref: Reference allele
            alt: Alternate allele

        Returns:
            African population allele frequency, or None if not found
        """
        variant_data = self.get_variant_frequency(chromosome, position, ref, alt)

        if variant_data is None:
            return None

        populations = variant_data.get("populations", {})

        # Try to get African/African American frequency
        # gnomAD v4 uses "afr" for African/African American
        if "afr" in populations:
            return populations["afr"].get("af")

        # Fallback to global frequency if AFR not available
        return variant_data.get("global_af")

    def get_population_summary(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str
    ) -> Dict:
        """
        Get a summary of all population frequencies

        Returns a formatted summary for display/logging
        """
        variant_data = self.get_variant_frequency(chromosome, position, ref, alt)

        if variant_data is None:
            return {
                "found": False,
                "message": "Variant not found in gnomAD"
            }

        populations = variant_data.get("populations", {})

        summary = {
            "found": True,
            "variant_id": variant_data["variant_id"],
            "global": {
                "af": variant_data.get("global_af", 0),
                "ac": variant_data.get("global_ac", 0),
                "an": variant_data.get("global_an", 0)
            },
            "african": populations.get("afr", {}).get("af", 0) if "afr" in populations else None,
            "european": populations.get("nfe", {}).get("af", 0) if "nfe" in populations else None,
            "east_asian": populations.get("eas", {}).get("af", 0) if "eas" in populations else None,
            "south_asian": populations.get("sas", {}).get("af", 0) if "sas" in populations else None,
        }

        return summary


# Quick test
if __name__ == "__main__":
    print("🧪 Testing gnomAD API Integration...")

    api = GnomADAPI()

    # Test with a known BRCA1 variant
    print("\n📍 Testing BRCA1 variant: chr17:43045677 G>A")

    # Get African frequency
    af_afr = api.get_african_frequency(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A"
    )

    if af_afr is not None:
        print(f"\n✅ African Population Frequency: {af_afr:.6f} ({af_afr * 100:.4f}%)")
    else:
        print("\n⚠️  Variant not found in gnomAD or no AFR frequency available")

    # Get full population summary
    print("\n📊 Full Population Summary:")
    summary = api.get_population_summary(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A"
    )

    if summary["found"]:
        print(f"   Variant ID: {summary['variant_id']}")
        print(f"   Global AF: {summary['global']['af']:.6f}" if summary['global']['af'] else "   Global AF: Not found")
        print(f"   African AF: {summary['african']:.6f}" if summary['african'] else "   African AF: Not available")
        print(f"   European AF: {summary['european']:.6f}" if summary['european'] else "   European AF: Not available")
    else:
        print(f"   {summary['message']}")

    # Test with a common benign variant
    print("\n\n📍 Testing common benign variant: chr17:43044295 G>A")
    af_afr_common = api.get_african_frequency(
        chromosome="17",
        position=43044295,
        ref="G",
        alt="A"
    )

    if af_afr_common is not None:
        print(f"✅ African Frequency: {af_afr_common:.6f} ({af_afr_common * 100:.4f}%)")

        # Show how this affects classification
        if af_afr_common > 0.05:
            print("   🟢 Strong evidence for benign (AF > 5%)")
        elif af_afr_common > 0.01:
            print("   🟡 Moderate evidence for benign (AF > 1%)")
        elif af_afr_common > 0.005:
            print("   🟠 Mild evidence for benign (AF > 0.5%)")
        else:
            print("   🔴 Rare variant (AF < 0.5%)")
    else:
        print("⚠️  Variant not found")

    print("\n✅ gnomAD API test complete!")
