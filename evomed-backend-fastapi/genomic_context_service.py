"""
Genomic Context Service

This module provides enriched genomic context for variants including:
- Regional classification (coding, non-coding, regulatory, etc.)
- Conservation scores (phyloP, phastCons)
- Functional annotations via Ensembl VEP
- Integration with multiple population databases

Enhances variant interpretation with comprehensive genomic context.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import modal
import requests

# Modal volume for caching
context_volume = modal.Volume.from_name("genomic_context_cache", create_if_missing=True)
CONTEXT_DB_PATH = "/genomic_context_cache/genomic_context.db"


class GenomicContextService:
    """
    Service for fetching and managing genomic context information

    Integrates multiple data sources:
    - Ensembl VEP for variant consequences and region types
    - 1000 Genomes for additional population frequencies
    - UCSC for conservation scores (when available)
    """

    def __init__(self):
        """Initialize the genomic context service"""
        self.ensembl_api_url = "https://rest.ensembl.org"
        self.cache_expiry_days = 90  # Genomic context changes less frequently
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for genomic context caching"""
        try:
            conn = sqlite3.connect(CONTEXT_DB_PATH)

            # Table for variant consequences and region types
            conn.execute("""
                CREATE TABLE IF NOT EXISTS variant_context (
                    chromosome TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    reference TEXT NOT NULL,
                    alternative TEXT NOT NULL,
                    region_type TEXT,
                    consequence_terms TEXT,
                    impact TEXT,
                    gene_symbol TEXT,
                    gene_id TEXT,
                    biotype TEXT,
                    is_coding INTEGER DEFAULT 0,
                    is_regulatory INTEGER DEFAULT 0,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chromosome, position, reference, alternative)
                )
            """)

            # Table for 1000 Genomes frequencies
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kg1000_frequencies (
                    chromosome TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    reference TEXT NOT NULL,
                    alternative TEXT NOT NULL,
                    african_af REAL,
                    african_ac INTEGER,
                    african_an INTEGER,
                    global_af REAL,
                    populations TEXT,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chromosome, position, reference, alternative)
                )
            """)

            # Indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_lookup
                ON variant_context (chromosome, position, reference, alternative)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_kg1000_lookup
                ON kg1000_frequencies (chromosome, position, reference, alternative)
            """)

            conn.commit()
            conn.close()
            print("Genomic context database initialized successfully")

        except Exception as e:
            print(f"Error initializing genomic context database: {e}")
            raise

    def get_variant_consequence(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """
        Fetch variant consequence and region type from Ensembl VEP

        Args:
            chromosome: Chromosome (with or without 'chr' prefix)
            position: Genomic position
            reference: Reference allele
            alternative: Alternative allele

        Returns:
            Dictionary containing consequence data or None
        """
        # Check cache first
        cached = self._get_cached_context(chromosome, position, reference, alternative)
        if cached:
            return cached

        # Normalize chromosome format (Ensembl expects without 'chr')
        chrom = chromosome.replace("chr", "")

        # Build VEP region format: chr:start-end:strand/alleles
        # For SNVs: chr:pos-pos:1/REF/ALT
        region = f"{chrom}:{position}-{position}:1/{reference}/{alternative}"

        try:
            print(
                f"Fetching variant consequence from Ensembl VEP for {chromosome}:{position}:{reference}>{alternative}"
            )
            print(f"VEP region string: {region}")

            url = f"{self.ensembl_api_url}/vep/human/region/{region}"
            headers = {"Content-Type": "application/json"}

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 400:
                print(f"VEP 400 error response: {response.text[:200]}")
                return None

            if response.status_code != 200:
                print(f"Ensembl VEP API error: HTTP {response.status_code}")
                return None

            data = response.json()

            if not data or len(data) == 0:
                print(f"No consequence data found for variant")
                return None

            # Parse the first result (most relevant)
            variant_data = data[0]

            # Extract consequence information
            consequences = variant_data.get("transcript_consequences", [])
            regulatory_features = variant_data.get(
                "regulatory_feature_consequences", []
            )
            intergenic = variant_data.get("intergenic_consequences", [])

            # Determine region type and coding status
            region_type = "intergenic"
            is_coding = False
            is_regulatory = False
            consequence_terms = []
            impact = "MODIFIER"
            gene_symbol = None
            gene_id = None
            biotype = None

            # Check transcript consequences (coding/non-coding genes)
            if consequences:
                top_consequence = consequences[0]
                consequence_terms = top_consequence.get("consequence_terms", [])
                impact = top_consequence.get("impact", "MODIFIER")
                gene_symbol = top_consequence.get("gene_symbol")
                gene_id = top_consequence.get("gene_id")
                biotype = top_consequence.get("biotype", "")

                # Determine if coding
                coding_consequences = [
                    "missense_variant",
                    "synonymous_variant",
                    "stop_gained",
                    "stop_lost",
                    "start_lost",
                    "frameshift_variant",
                    "inframe_insertion",
                    "inframe_deletion",
                    "protein_altering_variant",
                ]

                is_coding = any(
                    term in coding_consequences for term in consequence_terms
                )

                if is_coding:
                    region_type = "coding"
                elif "protein_coding" in biotype:
                    region_type = "non_coding_in_gene"  # UTR, intron, etc.
                else:
                    region_type = "non_coding_transcript"

            # Check regulatory features
            elif regulatory_features:
                region_type = "regulatory"
                is_regulatory = True
                reg_feature = regulatory_features[0]
                consequence_terms = reg_feature.get("consequence_terms", [])
                impact = reg_feature.get("impact", "MODIFIER")
                biotype = reg_feature.get("biotype", "")

            # Intergenic
            elif intergenic:
                region_type = "intergenic"
                consequence_terms = ["intergenic_variant"]

            result = {
                "region_type": region_type,
                "consequence_terms": consequence_terms,
                "impact": impact,
                "gene_symbol": gene_symbol,
                "gene_id": gene_id,
                "biotype": biotype,
                "is_coding": is_coding,
                "is_regulatory": is_regulatory,
                "raw_data": variant_data,  # Store full data for reference
            }

            # Cache the result
            self._cache_context(chromosome, position, reference, alternative, result)

            print(
                f"Variant consequence: {region_type}, coding={is_coding}, impact={impact}"
            )
            return result

        except requests.exceptions.Timeout:
            print("Ensembl VEP API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ensembl VEP API request error: {e}")
            return None
        except Exception as e:
            print(f"Error processing Ensembl VEP response: {e}")
            return None

    def get_1000genomes_frequency(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """
        Fetch variant frequency from 1000 Genomes via Ensembl

        Args:
            chromosome: Chromosome
            position: Genomic position
            reference: Reference allele
            alternative: Alternative allele

        Returns:
            Dictionary containing frequency data or None
        """
        # Check cache first
        cached = self._get_cached_kg1000(chromosome, position, reference, alternative)
        if cached:
            return cached

        # Normalize chromosome
        chrom = chromosome.replace("chr", "")

        try:
            print(
                f"Fetching 1000 Genomes frequency for {chromosome}:{position}:{reference}>{alternative}"
            )

            # Use Ensembl variant endpoint which includes 1000G data
            # Format: rs# or chr:pos:alleles (e.g., "17:47867177:A:G")
            variant_id = f"{chrom}:{position}:{reference}:{alternative}"
            print(f"1000G variant ID: {variant_id}")

            url = f"{self.ensembl_api_url}/variation/human/{variant_id}"
            headers = {"Content-Type": "application/json"}
            params = {"populations": 1}

            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 400:
                print(f"Ensembl variant API 400 error: {response.text[:200]}")
                return None

            if response.status_code != 200:
                print(f"Ensembl variant API error: HTTP {response.status_code}")
                return None

            data = response.json()

            # Extract population frequencies
            populations = data.get("populations", [])

            if not populations:
                print("No 1000 Genomes frequency data available")
                return None

            # Aggregate African populations from 1000G
            african_pops = [
                "YRI",
                "LWK",
                "GWD",
                "MSL",
                "ESN",
                "ACB",
                "ASW",
            ]  # 1000G African codes

            african_ac = 0
            african_an = 0
            global_ac = 0
            global_an = 0

            pop_details = {}

            for pop in populations:
                pop_name = pop.get("population")
                frequency = pop.get("frequency")
                allele_count = pop.get("allele_count", 0)
                allele_number = pop.get("allele_number", 0)

                if pop_name in african_pops:
                    african_ac += allele_count
                    african_an += allele_number
                    pop_details[pop_name] = frequency

                # Aggregate global (all populations)
                if pop_name == "1000GENOMES:phase_3:ALL":
                    global_ac = allele_count
                    global_an = allele_number

            # Calculate African allele frequency
            african_af = african_ac / african_an if african_an > 0 else 0.0
            global_af = global_ac / global_an if global_an > 0 else 0.0

            result = {
                "african_af": african_af,
                "african_ac": african_ac,
                "african_an": african_an,
                "global_af": global_af,
                "populations": pop_details,
                "source": "1000genomes_phase3",
            }

            # Cache the result
            self._cache_kg1000(chromosome, position, reference, alternative, result)

            print(
                f"1000 Genomes: African AF={african_af:.6f}, Global AF={global_af:.6f}"
            )
            return result

        except Exception as e:
            print(f"Error fetching 1000 Genomes data: {e}")
            return None

    def _get_cached_context(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """Check cache for variant context"""
        try:
            conn = sqlite3.connect(CONTEXT_DB_PATH)
            cursor = conn.execute(
                """SELECT region_type, consequence_terms, impact, gene_symbol,
                   gene_id, biotype, is_coding, is_regulatory, cached_at
                   FROM variant_context
                   WHERE chromosome=? AND position=? AND reference=? AND alternative=?""",
                (chromosome, position, reference, alternative),
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                (
                    region_type,
                    consequence_terms,
                    impact,
                    gene_symbol,
                    gene_id,
                    biotype,
                    is_coding,
                    is_regulatory,
                    cached_at,
                ) = result

                # Check if cache is still valid
                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time < timedelta(
                    days=self.cache_expiry_days
                ):
                    print(f"Using cached context for {chromosome}:{position}")
                    return {
                        "region_type": region_type,
                        "consequence_terms": consequence_terms.split(",")
                        if consequence_terms
                        else [],
                        "impact": impact,
                        "gene_symbol": gene_symbol,
                        "gene_id": gene_id,
                        "biotype": biotype,
                        "is_coding": bool(is_coding),
                        "is_regulatory": bool(is_regulatory),
                        "cached": True,
                    }
            return None
        except Exception as e:
            print(f"Error checking context cache: {e}")
            return None

    def _cache_context(
        self,
        chromosome: str,
        position: int,
        reference: str,
        alternative: str,
        context: Dict,
    ):
        """Cache variant context"""
        try:
            conn = sqlite3.connect(CONTEXT_DB_PATH)
            consequence_terms_str = ",".join(context.get("consequence_terms", []))

            conn.execute(
                """
                INSERT OR REPLACE INTO variant_context
                (chromosome, position, reference, alternative, region_type,
                 consequence_terms, impact, gene_symbol, gene_id, biotype,
                 is_coding, is_regulatory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    chromosome,
                    position,
                    reference,
                    alternative,
                    context.get("region_type"),
                    consequence_terms_str,
                    context.get("impact"),
                    context.get("gene_symbol"),
                    context.get("gene_id"),
                    context.get("biotype"),
                    1 if context.get("is_coding") else 0,
                    1 if context.get("is_regulatory") else 0,
                ),
            )

            conn.commit()
            conn.close()
            print(f"Cached context for {chromosome}:{position}")
        except Exception as e:
            print(f"Error caching context: {e}")

    def _get_cached_kg1000(
        self, chromosome: str, position: int, reference: str, alternative: str
    ) -> Optional[Dict]:
        """Check cache for 1000 Genomes data"""
        try:
            conn = sqlite3.connect(CONTEXT_DB_PATH)
            cursor = conn.execute(
                """SELECT african_af, african_ac, african_an, global_af,
                   populations, cached_at
                   FROM kg1000_frequencies
                   WHERE chromosome=? AND position=? AND reference=? AND alternative=?""",
                (chromosome, position, reference, alternative),
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                (
                    african_af,
                    african_ac,
                    african_an,
                    global_af,
                    populations,
                    cached_at,
                ) = result

                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time < timedelta(
                    days=self.cache_expiry_days
                ):
                    print(f"Using cached 1000G data for {chromosome}:{position}")
                    import json

                    return {
                        "african_af": african_af,
                        "african_ac": african_ac,
                        "african_an": african_an,
                        "global_af": global_af,
                        "populations": json.loads(populations) if populations else {},
                        "source": "1000genomes_phase3",
                        "cached": True,
                    }
            return None
        except Exception as e:
            print(f"Error checking 1000G cache: {e}")
            return None

    def _cache_kg1000(
        self,
        chromosome: str,
        position: int,
        reference: str,
        alternative: str,
        freq_data: Dict,
    ):
        """Cache 1000 Genomes frequency data"""
        try:
            import json

            conn = sqlite3.connect(CONTEXT_DB_PATH)

            populations_str = json.dumps(freq_data.get("populations", {}))

            conn.execute(
                """
                INSERT OR REPLACE INTO kg1000_frequencies
                (chromosome, position, reference, alternative, african_af,
                 african_ac, african_an, global_af, populations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    chromosome,
                    position,
                    reference,
                    alternative,
                    freq_data.get("african_af"),
                    freq_data.get("african_ac"),
                    freq_data.get("african_an"),
                    freq_data.get("global_af"),
                    populations_str,
                ),
            )

            conn.commit()
            conn.close()
            print(f"Cached 1000G data for {chromosome}:{position}")
        except Exception as e:
            print(f"Error caching 1000G data: {e}")
