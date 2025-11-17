"""
BRCA Exchange API Service

This module provides a service for querying the BRCA Exchange API directly
without downloading data locally. This ensures always-current data and reduces
storage requirements.

API Documentation: https://github.com/BRCAChallenge/brca-exchange/blob/master/website/content/api_docs/api_overview.md
"""

import time
from typing import Any, Dict, List, Optional

import requests


class BRCAExchangeAPI:
    """
    Service for interacting with the BRCA Exchange API

    The BRCA Exchange provides comprehensive variant data from multiple sources:
    - ClinVar: Clinical variant interpretations
    - ENIGMA: Expert-curated BRCA variants
    - gnomAD: Population frequencies including African populations
    - ExAC: Exome aggregation data
    - 1000 Genomes: Population diversity data
    """

    def __init__(self):
        """Initialize BRCA Exchange API service"""
        self.base_url = "https://brcaexchange.org/backend/data/"
        self.timeout = 30  # seconds
        self.cache = {}  # Simple in-memory cache

    def search_variants(
        self,
        gene_symbol: Optional[str] = None,
        genomic_hgvs: Optional[str] = None,
        search_term: Optional[str] = None,
        chromosome: Optional[str] = None,
        position: Optional[int] = None,
        include_sources: List[str] = None,
        page_size: int = 100,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Search for variants in BRCA Exchange

        Args:
            gene_symbol: Filter by gene (e.g., "BRCA1", "BRCA2")
            genomic_hgvs: Search by HGVS notation (e.g., "chr17:g.43094487G>A")
            search_term: Free text search across most fields
            chromosome: Filter by chromosome
            position: Filter by genomic position
            include_sources: List of sources to include (default: all)
                Options: "Variant_in_ENIGMA", "Variant_in_ClinVar",
                         "Variant_in_GnomAD", "Variant_in_ExAC", etc.
            page_size: Number of results per page (0 = all)
            format: Response format ("json", "csv", "tsv")

        Returns:
            Dictionary containing:
                - count: Total number of variants
                - data: List of variant records
                - releaseName: Current release name
        """
        params = {
            "format": format,
            "page_size": str(page_size),
        }

        # Add data source inclusion
        if include_sources:
            params["include[]"] = include_sources
        else:
            params["include[]"] = "all"

        # Add filters
        filters = []
        filter_values = []

        if gene_symbol:
            filters.append("Gene_Symbol")
            filter_values.append(gene_symbol)

        if chromosome:
            filters.append("Chr")
            filter_values.append(chromosome)

        if position:
            filters.append("Pos")
            filter_values.append(str(position))

        if filters:
            params["filter[]"] = filters
            params["filterValue[]"] = filter_values

        # Add search term if provided
        if search_term:
            params["search_term"] = search_term

        if genomic_hgvs:
            params["search_term"] = genomic_hgvs

        try:
            print(f"Querying BRCA Exchange API: {params}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            if format == "json":
                return response.json()
            else:
                return {"data": response.text}

        except requests.exceptions.Timeout:
            return {"error": "API request timed out", "count": 0, "data": []}
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}", "count": 0, "data": []}
        except Exception as e:
            return {
                "error": f"Error processing response: {str(e)}",
                "count": 0,
                "data": [],
            }

    def get_variant_by_id(self, variant_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific variant

        Args:
            variant_id: Variant identifier

        Returns:
            Variant details including version history with changes
        """
        url = f"https://brcaexchange.org/backend/data/variant/"
        params = {"variant_id": variant_id}

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching variant {variant_id}: {e}")
            return None

    def get_variant_by_coordinates(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        gene_symbol: str = "BRCA1",
    ) -> Optional[Dict]:
        """
        Get variant information by genomic coordinates

        Args:
            chromosome: Chromosome (e.g., "17" or "chr17")
            position: Genomic position (1-based)
            ref: Reference allele
            alt: Alternative allele
            gene_symbol: Gene symbol (default: "BRCA1")

        Returns:
            Variant information if found, None otherwise
        """
        # Normalize chromosome format
        chrom = chromosome.replace("chr", "")

        # Create cache key
        cache_key = f"{chrom}:{position}:{ref}:{alt}"
        if cache_key in self.cache:
            print(f"Using cached variant data for {cache_key}")
            return self.cache[cache_key]

        # Search by coordinates
        result = self.search_variants(
            gene_symbol=gene_symbol, chromosome=chrom, position=position, page_size=100
        )

        if result.get("count", 0) == 0:
            return None

        # Find exact match by ref/alt
        variants = result.get("data", [])
        for variant in variants:
            # Check if this matches our ref/alt
            variant_ref = variant.get("Ref", "")
            variant_alt = variant.get("Alt", "")
            variant_pos = variant.get("Pos", "")

            if (
                str(variant_pos) == str(position)
                and variant_ref == ref
                and variant_alt == alt
            ):
                # Cache the result
                self.cache[cache_key] = variant
                return variant

        return None

    def get_african_frequency(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        gene_symbol: str = "BRCA1",
    ) -> Optional[Dict]:
        """
        Get African population frequency for a variant from BRCA Exchange

        This fetches data from gnomAD columns included in BRCA Exchange

        Args:
            chromosome: Chromosome identifier
            position: Genomic position
            ref: Reference allele
            alt: Alternative allele
            gene_symbol: Gene symbol

        Returns:
            Dictionary with African and global frequencies, or None
        """
        variant = self.get_variant_by_coordinates(
            chromosome, position, ref, alt, gene_symbol
        )

        if not variant:
            return None

        # Extract gnomAD frequency data
        # BRCA Exchange includes columns like:
        # - Allele_frequency_AFR (gnomAD African)
        # - Allele_frequency (global)

        african_af = None
        global_af = None

        # Try different column names that might contain African frequency
        african_col_names = [
            "Allele_frequency_AFR",
            "gnomAD_AFR",
            "AFR_AF",
            "Allele_frequency_AFR_v3",
        ]

        for col_name in african_col_names:
            if col_name in variant and variant[col_name]:
                try:
                    african_af = float(variant[col_name])
                    break
                except (ValueError, TypeError):
                    continue

        # Global frequency
        global_col_names = [
            "Allele_frequency",
            "gnomAD_AF",
            "AF",
        ]

        for col_name in global_col_names:
            if col_name in variant and variant[col_name]:
                try:
                    global_af = float(variant[col_name])
                    break
                except (ValueError, TypeError):
                    continue

        return {
            "african_af": african_af,
            "global_af": global_af,
            "source": "brca_exchange",
            "variant_data": variant,
        }

    def get_clinical_significance(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        gene_symbol: str = "BRCA1",
    ) -> Optional[Dict]:
        """
        Get clinical significance classification for a variant

        Args:
            chromosome: Chromosome identifier
            position: Genomic position
            ref: Reference allele
            alt: Alternative allele
            gene_symbol: Gene symbol

        Returns:
            Dictionary with clinical significance from multiple sources
        """
        variant = self.get_variant_by_coordinates(
            chromosome, position, ref, alt, gene_symbol
        )

        if not variant:
            return None

        # Extract clinical significance from various sources
        clinical_data = {
            "clinvar_classification": variant.get("Clinical_significance_ENIGMA"),
            "enigma_classification": variant.get("Clinical_Classification"),
            "pathogenicity_expert": variant.get("Pathogenicity_expert"),
            "pathogenicity_all": variant.get("Pathogenicity_all"),
            "variant_id": variant.get("id"),
        }

        return clinical_data

    def get_variant_reports(self, variant_id: str) -> List[Dict]:
        """
        Get clinical reports associated with a variant

        Args:
            variant_id: Variant identifier

        Returns:
            List of clinical reports from various sources
        """
        url = f"https://brcaexchange.org/backend/data/variant/{variant_id}/reports"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching reports for variant {variant_id}: {e}")
            return []

    def autocomplete_search(self, term: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for variant search

        Args:
            term: Partial search term
            limit: Maximum number of suggestions

        Returns:
            List of suggested search terms
        """
        url = "https://brcaexchange.org/backend/data/suggestions/"
        params = {"term": term, "limit": limit}

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching autocomplete suggestions: {e}")
            return []

    def get_database_stats(self) -> Dict:
        """
        Get summary statistics about BRCA Exchange database

        Returns:
            Dictionary with variant counts and database info
        """
        url = "https://brcaexchange.org/backend/data/variantcounts"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching database stats: {e}")
            return {}

    def clear_cache(self):
        """Clear the in-memory cache"""
        self.cache = {}
        print("Cache cleared")


# Example usage
if __name__ == "__main__":
    api = BRCAExchangeAPI()

    # Example 1: Search for BRCA1 variants
    print("\n=== Example 1: Search BRCA1 variants ===")
    result = api.search_variants(gene_symbol="BRCA1", page_size=5)
    print(f"Found {result.get('count', 0)} BRCA1 variants")
    if result.get("data"):
        print(f"First variant: {result['data'][0].get('id')}")

    # Example 2: Get variant by coordinates
    print("\n=== Example 2: Get variant by coordinates ===")
    variant = api.get_variant_by_coordinates(
        chromosome="17", position=43094487, ref="G", alt="A", gene_symbol="BRCA1"
    )
    if variant:
        print(f"Found variant: {variant.get('id')}")

    # Example 3: Get African frequency
    print("\n=== Example 3: Get African population frequency ===")
    freq_data = api.get_african_frequency(
        chromosome="17", position=43094487, ref="G", alt="A"
    )
    if freq_data:
        print(f"African AF: {freq_data.get('african_af')}")
        print(f"Global AF: {freq_data.get('global_af')}")

    # Example 4: Database stats
    print("\n=== Example 4: Database statistics ===")
    stats = api.get_database_stats()
    print(f"Database stats: {stats}")
