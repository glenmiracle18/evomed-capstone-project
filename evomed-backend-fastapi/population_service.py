"""
African Population Frequency Service

This module provides services for fetching and caching population-specific
variant frequencies, with a focus on African populations to address
genomic health equity in variant interpretation.

Key Features:
- gnomAD API integration for African population frequencies
- Local SQLite caching for performance
- Population-specific variant classification adjustments
- Support for reducing false positives in African populations
"""

import sqlite3
import requests
import json
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import modal

# Modal volume for persistent population data cache
population_volume = modal.Volume.from_name("population_cache", create_if_missing=True)
POPULATION_DB_PATH = "/population_cache/african_frequencies.db"


class PopulationFrequencyService:
    """
    Service for fetching and managing population-specific variant frequencies

    This service integrates with gnomAD to fetch African population frequencies
    and provides local caching to improve performance and reduce API calls.
    """

    def __init__(self):
        """Initialize the population frequency service"""
        self.gnomad_api_url = "https://gnomad.broadinstitute.org/api"
        self.cache_expiry_days = 30  # Cache expires after 30 days
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for population frequency caching"""
        try:
            conn = sqlite3.connect(POPULATION_DB_PATH)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS african_frequencies (
                    chromosome TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    reference TEXT NOT NULL,
                    alternative TEXT NOT NULL,
                    african_ac INTEGER,
                    african_an INTEGER,
                    african_af REAL,
                    global_ac INTEGER,
                    global_an INTEGER,
                    global_af REAL,
                    source TEXT DEFAULT 'gnomad_v4',
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chromosome, position, reference, alternative)
                )
            """)

            # Create index for fast lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_variant_lookup
                ON african_frequencies (chromosome, position, reference, alternative)
            """)

            conn.commit()
            conn.close()
            print("Population frequency database initialized successfully")

        except Exception as e:
            print(f"Error initializing population database: {e}")
            raise

    def get_gnomad_frequency(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """
        Fetch variant frequency data from gnomAD GraphQL API

        Args:
            chromosome: Chromosome (e.g., 'chr17', '17')
            position: Genomic position (1-based)
            reference: Reference allele
            alternative: Alternative allele

        Returns:
            Dictionary containing African and global frequency data, or None if not found
        """

        # Normalize chromosome format (gnomAD expects without 'chr' prefix)
        chrom = chromosome.replace("chr", "")

        # Create variant ID in gnomAD format: chrom-pos-ref-alt
        variant_id = f"{chrom}-{position}-{reference}-{alternative}"

        query = """
        query VariantQuery($variantId: String!) {
          variant(variantId: $variantId, dataset: gnomad_r4) {
            variantId
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

        variables = {
            "variantId": variant_id,
        }

        try:
            print(
                f"Fetching gnomAD data for {chromosome}:{position}:{reference}>{alternative} (variant_id: {variant_id})"
            )

            response = requests.post(
                self.gnomad_api_url,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code != 200:
                print(f"gnomAD API error: HTTP {response.status_code}")
                return None

            data = response.json()

            if "errors" in data:
                print(f"gnomAD GraphQL errors: {data['errors']}")
                return None

            if not data.get("data") or not data["data"].get("variant"):
                print(
                    f"Variant not found in gnomAD: {chromosome}:{position}:{reference}>{alternative}"
                )
                return None

            variant_data = data["data"]["variant"]
            genome_data = variant_data.get("genome")

            if not genome_data:
                print("No genome data available for variant")
                return None

            # Extract African population frequency
            african_freq = None
            if genome_data.get("populations"):
                for pop in genome_data["populations"]:
                    if pop["id"] == "afr":  # African/African American population
                        ac = pop.get("ac", 0)
                        an = pop.get("an", 0)
                        af = ac / an if an > 0 else 0.0  # Calculate AF from AC/AN

                        african_freq = {
                            "ac": ac,
                            "an": an,
                            "af": af,
                        }
                        break

            # Calculate global AF from AC/AN
            global_ac = genome_data.get("ac", 0)
            global_an = genome_data.get("an", 0)
            global_af = global_ac / global_an if global_an > 0 else 0.0

            result = {
                "african": african_freq,
                "global": {
                    "ac": global_ac,
                    "an": global_an,
                    "af": global_af,
                },
            }

            print(
                f"Successfully fetched gnomAD data: African AF = {african_freq['af'] if african_freq else 'N/A'}, Global AF = {global_af}"
            )
            return result

        except requests.exceptions.Timeout:
            print("gnomAD API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"gnomAD API request error: {e}")
            return None
        except Exception as e:
            print(f"Error processing gnomAD response: {e}")
            return None

    def get_cached_frequency(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """
        Check local cache for variant frequency data

        Args:
            chromosome: Chromosome identifier
            position: Genomic position
            reference: Reference allele
            alternative: Alternative allele

        Returns:
            Cached frequency data or None if not found/expired
        """
        try:
            conn = sqlite3.connect(POPULATION_DB_PATH)
            cursor = conn.execute(
                """SELECT african_af, global_af, cached_at
                   FROM african_frequencies
                   WHERE chromosome=? AND position=? AND reference=? AND alternative=?""",
                (chromosome, position, reference, alternative),
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                african_af, global_af, cached_at = result

                # Check if cache is still valid (within expiry period)
                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time < timedelta(
                    days=self.cache_expiry_days
                ):
                    print(
                        f"Using cached frequency data for {chromosome}:{position}:{reference}>{alternative}"
                    )
                    return {
                        "african_af": african_af,
                        "global_af": global_af,
                        "cached": True,
                        "cached_at": cached_at,
                    }
                else:
                    print(
                        f"Cached data expired for {chromosome}:{position}:{reference}>{alternative}"
                    )

            return None

        except Exception as e:
            print(f"Error accessing frequency cache: {e}")
            return None

    def cache_frequency(
        self,
        chromosome: str,
        position: int,
        reference: str,
        alternative: str,
        freq_data: Dict,
    ):
        """
        Cache frequency data in local SQLite database

        Args:
            chromosome: Chromosome identifier
            position: Genomic position
            reference: Reference allele
            alternative: Alternative allele
            freq_data: Frequency data from gnomAD API
        """
        try:
            conn = sqlite3.connect(POPULATION_DB_PATH)

            african_data = freq_data.get("african")
            global_data = freq_data.get("global", {})

            african_ac = african_data["ac"] if african_data else None
            african_an = african_data["an"] if african_data else None
            african_af = african_data["af"] if african_data else None

            global_ac = global_data.get("ac")
            global_an = global_data.get("an")
            global_af = global_data.get("af")

            conn.execute(
                """INSERT OR REPLACE INTO african_frequencies
                   (chromosome, position, reference, alternative,
                    african_ac, african_an, african_af,
                    global_ac, global_an, global_af, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    chromosome,
                    position,
                    reference,
                    alternative,
                    african_ac,
                    african_an,
                    african_af,
                    global_ac,
                    global_an,
                    global_af,
                    "gnomad_v4",
                ),
            )
            conn.commit()
            conn.close()

            print(
                f"Cached frequency data for {chromosome}:{position}:{reference}>{alternative}"
            )

        except Exception as e:
            print(f"Error caching frequency data: {e}")

    def get_population_frequency(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Dict:
        """
        Main method to get population frequency with caching

        This method first checks the local cache, and if not found or expired,
        fetches fresh data from gnomAD API and caches it.

        Args:
            chromosome: Chromosome identifier
            position: Genomic position
            reference: Reference allele
            alternative: Alternative allele

        Returns:
            Dictionary containing frequency data and metadata
        """

        # Check cache first
        cached = self.get_cached_frequency(chromosome, position, reference, alternative)
        if cached:
            return cached

        # Fetch from gnomAD API
        print(
            f"Fetching fresh data from gnomAD for {chromosome}:{position}:{reference}>{alternative}"
        )
        freq_data = self.get_gnomad_frequency(
            chromosome, position, reference, alternative
        )

        if freq_data:
            # Cache the result
            self.cache_frequency(
                chromosome, position, reference, alternative, freq_data
            )

            african_data = freq_data.get("african")
            global_data = freq_data.get("global", {})

            return {
                "african_af": african_data["af"] if african_data else None,
                "global_af": global_data.get("af"),
                "cached": False,
                "source": "gnomad_v4",
            }

        # Return empty result if gnomAD lookup failed
        return {
            "african_af": None,
            "global_af": None,
            "cached": False,
            "source": None,
            "error": "Failed to fetch from gnomAD",
        }

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the frequency cache

        Returns:
            Dictionary containing cache statistics
        """
        try:
            conn = sqlite3.connect(POPULATION_DB_PATH)

            # Total cached variants
            cursor = conn.execute("SELECT COUNT(*) FROM african_frequencies")
            total_variants = cursor.fetchone()[0]

            # Variants with African frequency data
            cursor = conn.execute(
                "SELECT COUNT(*) FROM african_frequencies WHERE african_af IS NOT NULL"
            )
            african_variants = cursor.fetchone()[0]

            # Recent cache entries (last 7 days)
            cursor = conn.execute(
                "SELECT COUNT(*) FROM african_frequencies WHERE cached_at > datetime('now', '-7 days')"
            )
            recent_entries = cursor.fetchone()[0]

            conn.close()

            return {
                "total_cached_variants": total_variants,
                "variants_with_african_data": african_variants,
                "recent_cache_entries": recent_entries,
                "african_data_coverage": (african_variants / total_variants * 100)
                if total_variants > 0
                else 0,
            }

        except Exception as e:
            print(f"Error getting cache statistics: {e}")
            return {"error": str(e)}


def calculate_population_adjustment(
    delta_score: float, freq_data: Optional[Dict], use_african_adjustment: bool
) -> Tuple[float, float, str]:
    """
    Calculate population-specific adjustment to Evo2 delta score

    This function implements the core logic for adjusting variant pathogenicity
    predictions based on African population frequencies to reduce false positives.

    Args:
        delta_score: Original Evo2 delta score
        freq_data: Population frequency data from gnomAD
        use_african_adjustment: Whether to apply African population adjustments

    Returns:
        Tuple of (adjusted_score, adjustment_value, reasoning)
    """

    if not use_african_adjustment or not freq_data:
        return delta_score, 0.0, "No population adjustment applied"

    african_af = freq_data.get("african_af")
    global_af = freq_data.get("global_af", 0.0)

    if african_af is None:
        return delta_score, 0.0, "No African population frequency data available"

    # Population adjustment algorithm
    population_adjustment = 0.0
    reasoning_parts = []

    # Rule 1: High frequency in African populations (strong benign evidence)
    if african_af > 0.05:  # 5% frequency threshold
        adjustment = 0.004  # Strong push towards benign
        population_adjustment += adjustment
        reasoning_parts.append(
            f"Common in African populations (AF={african_af:.4f}, +{adjustment:.4f})"
        )

    elif african_af > 0.01:  # 1% frequency threshold
        adjustment = 0.002  # Moderate push towards benign
        population_adjustment += adjustment
        reasoning_parts.append(
            f"Present in African populations (AF={african_af:.4f}, +{adjustment:.4f})"
        )

    elif african_af > 0.005:  # 0.5% frequency threshold
        adjustment = 0.001  # Mild push towards benign
        population_adjustment += adjustment
        reasoning_parts.append(
            f"Low frequency in African populations (AF={african_af:.4f}, +{adjustment:.4f})"
        )

    # Rule 2: African-specific variants (rare globally but common in Africans)
    if african_af > 0.01 and global_af < 0.001:
        adjustment = (
            0.003  # Additional benign evidence for population-specific variants
        )
        population_adjustment += adjustment
        reasoning_parts.append(
            f"African population-specific variant (+{adjustment:.4f})"
        )

    # Rule 3: Population stratification artifacts
    if african_af < 0.0001 and global_af > 0.01:
        adjustment = -0.001  # Slight increase in pathogenicity concern
        population_adjustment += adjustment
        reasoning_parts.append(
            f"Possible population stratification artifact ({adjustment:.4f})"
        )

    # Rule 4: Known protective variants (e.g., malaria resistance)
    if is_known_protective_variant(freq_data):
        adjustment = 0.005  # Strong benign adjustment for protective variants
        population_adjustment += adjustment
        reasoning_parts.append(f"Known protective variant (+{adjustment:.4f})")

    adjusted_score = delta_score + population_adjustment
    reasoning = (
        "; ".join(reasoning_parts)
        if reasoning_parts
        else "Standard population frequency"
    )

    return adjusted_score, population_adjustment, reasoning


def is_known_protective_variant(freq_data: Dict) -> bool:
    """
    Check if variant is a known protective variant (e.g., malaria resistance)

    This is a placeholder for future implementation of protective variant detection.
    Could be expanded to include known variants like HbS, HbC, G6PD deficiency, etc.

    Args:
        freq_data: Population frequency data

    Returns:
        True if variant is known to be protective, False otherwise
    """
    # Placeholder implementation
    # In a full implementation, this would check against a database of
    # known protective variants (malaria resistance, etc.)
    return False


def classify_variant_with_population(
    adjusted_score: float,
    original_score: float,
    freq_data: Optional[Dict],
    population_adjustment: float,
    adjustment_reasoning: str,
) -> Dict:
    """
    Classify variant using population-adjusted thresholds and scores

    Args:
        adjusted_score: Population-adjusted Evo2 score
        original_score: Original Evo2 delta score
        freq_data: Population frequency data
        population_adjustment: Applied population adjustment
        adjustment_reasoning: Explanation of adjustment

    Returns:
        Dictionary containing classification results
    """

    # Base threshold from BRCA1 calibration
    base_threshold = -0.0009178519

    # Adjust threshold based on population context
    if freq_data and freq_data.get("african_af"):
        african_af = freq_data["african_af"]

        if african_af > 0.05:
            # High African frequency - use more lenient threshold
            threshold = base_threshold - 0.002
            method = "african_high_frequency_adjusted"
            context = f"High frequency in African populations (AF={african_af:.4f})"

        elif african_af > 0.01:
            # Moderate African frequency
            threshold = base_threshold - 0.001
            method = "african_moderate_frequency_adjusted"
            context = f"Moderate frequency in African populations (AF={african_af:.4f})"

        else:
            # Standard threshold with population awareness
            threshold = base_threshold
            method = "standard_with_african_context"
            context = f"Rare in African populations (AF={african_af:.4f})"
    else:
        threshold = base_threshold
        method = "standard_evo2"
        context = "No African population frequency data available"

    # Classification based on adjusted score
    if adjusted_score < threshold:
        prediction = "Likely pathogenic"
        # Calculate confidence using loss-of-function standard deviation
        lof_std = 0.0015140239
        confidence = min(1.0, abs(adjusted_score - threshold) / lof_std)
    else:
        prediction = "Likely benign"
        # Calculate confidence using functional standard deviation
        func_std = 0.0009016589
        confidence = min(1.0, abs(adjusted_score - threshold) / func_std)

    return {
        "prediction": prediction,
        "confidence": float(confidence),
        "method": method,
        "context": context,
        "threshold_used": float(threshold),
        "original_score": float(original_score),
        "adjusted_score": float(adjusted_score),
        "population_adjustment": float(population_adjustment),
        "adjustment_reasoning": adjustment_reasoning,
    }
