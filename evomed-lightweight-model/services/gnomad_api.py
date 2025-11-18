"""
gnomAD API integration for African population frequency data
Uses gnomAD REST API for reliable variant frequency lookups
"""

import requests
from typing import Optional, Dict
import time


class GnomADAPI:
    """Fetch population frequency data from gnomAD using REST API"""

    def __init__(self, cache_enabled: bool = True):
        # Use gnomAD REST API endpoint
        self.base_url = "https://gnomad.broadinstitute.org/api"
        self.cache_enabled = cache_enabled
        self.cache = {}

    def get_variant_frequency(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        dataset: str = "gnomad_r4"
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

        # Create variant ID in gnomAD format
        variant_id = f"{chrom}-{position}-{ref}-{alt}"

        # Check cache
        if self.cache_enabled and variant_id in self.cache:
            return self.cache[variant_id]

        # Updated GraphQL query for gnomAD v4
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
              ac_hom
              faf95 {
                popmax
                popmax_population
              }
              populations {
                id
                ac
                an
                af
                ac_hom
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
                self.base_url,
                json={"query": query, "variables": variables},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=15
            )

            # Check for errors
            if response.status_code != 200:
                print(f"⚠️  gnomAD API returned status {response.status_code}")
                return None

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                print(f"⚠️  gnomAD GraphQL errors: {data['errors']}")
                return None

            # Parse response
            if "data" in data and data["data"].get("variant"):
                variant_data = data["data"]["variant"]
                genome_data = variant_data.get("genome", {})

                if not genome_data:
                    # Try exome data if genome not available
                    genome_data = variant_data.get("exome", {})

                if not genome_data:
                    return None

                # Extract population frequencies
                populations = genome_data.get("populations", [])

                # Build result dictionary
                result = {
                    "variant_id": variant_id,
                    "chromosome": variant_data.get("chrom"),
                    "position": variant_data.get("pos"),
                    "ref": variant_data.get("ref"),
                    "alt": variant_data.get("alt"),
                    "global_af": genome_data.get("af"),
                    "global_ac": genome_data.get("ac"),
                    "global_an": genome_data.get("an"),
                    "global_hom": genome_data.get("ac_hom"),
                    "populations": {}
                }

                # Extract specific population frequencies
                for pop in populations:
                    pop_id = pop.get("id")
                    if pop_id:
                        result["populations"][pop_id] = {
                            "af": pop.get("af"),
                            "ac": pop.get("ac"),
                            "an": pop.get("an"),
                            "hom": pop.get("ac_hom")
                        }

                # Cache the result
                if self.cache_enabled:
                    self.cache[variant_id] = result

                return result
            else:
                # Variant not found in gnomAD
                return None

        except requests.exceptions.Timeout:
            print(f"⚠️  gnomAD API timeout for {variant_id}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️  gnomAD API error for {variant_id}: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Unexpected error querying gnomAD for {variant_id}: {e}")
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
        global_af = variant_data.get("global_af")
        if global_af is not None:
            print(f"   ℹ️  No AFR frequency, using global: {global_af:.6f}")
        return global_af

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
                "af": variant_data.get("global_af"),
                "ac": variant_data.get("global_ac"),
                "an": variant_data.get("global_an"),
                "hom": variant_data.get("global_hom")
            },
            "african": populations.get("afr", {}).get("af") if "afr" in populations else None,
            "european": populations.get("nfe", {}).get("af") if "nfe" in populations else None,
            "east_asian": populations.get("eas", {}).get("af") if "eas" in populations else None,
            "south_asian": populations.get("sas", {}).get("af") if "sas" in populations else None,
            "latino": populations.get("amr", {}).get("af") if "amr" in populations else None,
        }

        return summary


# Quick test
if __name__ == "__main__":
    print("🧪 Testing gnomAD API Integration...")

    api = GnomADAPI()

    # Test with a more common variant that's likely in gnomAD
    print("\n📍 Testing common BRCA1 variant: chr17:43094464 A>C")
    print("   (This is a known benign variant)")

    af_afr = api.get_african_frequency(
        chromosome="17",
        position=43094464,
        ref="A",
        alt="C"
    )

    if af_afr is not None:
        print(f"\n✅ African Population Frequency: {af_afr:.6f} ({af_afr * 100:.4f}%)")

        if af_afr > 0.01:
            print("   🟢 Common in African population - strong benign evidence")
        elif af_afr > 0.001:
            print("   🟡 Present in African population - moderate benign evidence")
        else:
            print("   🔴 Rare in African population")
    else:
        print("\n⚠️  Variant not found in gnomAD")

    # Get full population summary
    print("\n📊 Full Population Summary:")
    summary = api.get_population_summary(
        chromosome="17",
        position=43094464,
        ref="A",
        alt="C"
    )

    if summary["found"]:
        print(f"   Variant ID: {summary['variant_id']}")
        if summary['global']['af']:
            print(f"   Global AF: {summary['global']['af']:.6f} ({summary['global']['af']*100:.4f}%)")
        if summary['african']:
            print(f"   African AF: {summary['african']:.6f} ({summary['african']*100:.4f}%)")
        if summary['european']:
            print(f"   European AF: {summary['european']:.6f} ({summary['european']*100:.4f}%)")
        if summary['east_asian']:
            print(f"   East Asian AF: {summary['east_asian']:.6f} ({summary['east_asian']*100:.4f}%)")
    else:
        print(f"   {summary['message']}")

    # Test with another variant
    print("\n\n📍 Testing rs80357906 (BRCA1): chr17:43057051 T>C")

    af_afr2 = api.get_african_frequency(
        chromosome="17",
        position=43057051,
        ref="T",
        alt="C"
    )

    if af_afr2 is not None:
        print(f"✅ African Frequency: {af_afr2:.6f} ({af_afr2 * 100:.4f}%)")
    else:
        print("⚠️  Variant not found in gnomAD (may be rare pathogenic)")

    print("\n✅ gnomAD API test complete!")
    print("\nNOTE: If variants aren't found, this is normal for:")
    print("  - Very rare pathogenic variants")
    print("  - De novo mutations")
    print("  - Variants not in gnomAD's sequenced populations")
