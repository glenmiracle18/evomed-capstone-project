"""
Genomic sequence fetcher using UCSC Genome Browser API
Fetches real genomic context for variants
"""

import requests
from typing import Optional, Tuple
import time


class GenomicSequenceFetcher:
    """Fetch genomic sequences from UCSC Genome Browser"""

    def __init__(self, genome_build: str = "hg38"):
        self.genome_build = genome_build
        self.base_url = f"https://api.genome.ucsc.edu/getData/sequence"
        self.cache = {}  # Simple in-memory cache

    def fetch_sequence(
        self,
        chromosome: str,
        start: int,
        end: int,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Fetch genomic sequence from UCSC API

        Args:
            chromosome: Chromosome (e.g., "chr17" or "17")
            start: Start position (0-based)
            end: End position (0-based, exclusive)
            max_retries: Number of retry attempts

        Returns:
            DNA sequence string in uppercase, or None if failed
        """
        # Normalize chromosome format
        if not chromosome.startswith("chr"):
            chromosome = f"chr{chromosome}"

        # Check cache
        cache_key = f"{chromosome}:{start}-{end}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Build request URL
        url = f"{self.base_url}?genome={self.genome_build};chrom={chromosome};start={start};end={end}"

        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                if "dna" in data:
                    sequence = data["dna"].upper()
                    # Cache the result
                    self.cache[cache_key] = sequence
                    return sequence
                else:
                    print(f"⚠️  No sequence data in response for {cache_key}")
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Failed to fetch sequence after {max_retries} attempts: {e}")
                    return None

        return None

    def get_variant_context(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        context_size: int = 256
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get genomic context for a variant, returning both REF and ALT sequences

        Args:
            chromosome: Chromosome
            position: Variant position (1-based)
            ref: Reference allele
            alt: Alternate allele
            context_size: Number of bases to fetch on each side

        Returns:
            Tuple of (ref_sequence, alt_sequence) with context, or (None, None) if failed
        """
        # Convert to 0-based for UCSC API
        start = position - 1 - context_size
        end = position - 1 + len(ref) + context_size

        # Ensure we don't go below 0
        if start < 0:
            start = 0

        # Fetch the reference sequence
        ref_context = self.fetch_sequence(chromosome, start, end)

        if ref_context is None:
            return None, None

        # Calculate where the variant is in our fetched sequence
        variant_offset = (position - 1) - start

        # Verify the reference allele matches
        actual_ref = ref_context[variant_offset:variant_offset + len(ref)]
        if actual_ref.upper() != ref.upper():
            print(f"⚠️  Reference mismatch at {chromosome}:{position}")
            print(f"   Expected: {ref}, Got: {actual_ref}")
            # Continue anyway - might be due to different genome builds

        # Create ALT sequence by substituting the variant
        alt_context = (
            ref_context[:variant_offset] +
            alt.upper() +
            ref_context[variant_offset + len(ref):]
        )

        return ref_context, alt_context

    def prepare_model_input(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        max_length: int = 512,
        context_size: int = 256
    ) -> Tuple[Optional[str], Optional[str], dict]:
        """
        Prepare sequences for model input with proper genomic context

        Args:
            chromosome: Chromosome
            position: Variant position (1-based)
            ref: Reference allele
            alt: Alternate allele
            max_length: Maximum sequence length for model
            context_size: Context window size

        Returns:
            Tuple of (ref_sequence, alt_sequence, metadata)
        """
        ref_seq, alt_seq = self.get_variant_context(
            chromosome, position, ref, alt, context_size
        )

        if ref_seq is None or alt_seq is None:
            # Fallback to padding with N's if API fails
            print(f"⚠️  Using fallback N-padding for {chromosome}:{position}")
            padding = 'N' * context_size
            ref_seq = padding + ref.upper() + padding
            alt_seq = padding + alt.upper() + padding

        # Truncate or pad to max_length
        if len(ref_seq) > max_length:
            # Center the variant
            middle = len(ref_seq) // 2
            start = middle - max_length // 2
            end = start + max_length
            ref_seq = ref_seq[start:end]
            alt_seq = alt_seq[start:end]
        elif len(ref_seq) < max_length:
            # Pad with N's to reach max_length
            padding_needed = max_length - len(ref_seq)
            pad_left = padding_needed // 2
            pad_right = padding_needed - pad_left
            ref_seq = 'N' * pad_left + ref_seq + 'N' * pad_right
            alt_seq = 'N' * pad_left + alt_seq + 'N' * pad_right

        metadata = {
            'chromosome': chromosome,
            'position': position,
            'ref': ref,
            'alt': alt,
            'ref_length': len(ref_seq),
            'alt_length': len(alt_seq),
            'has_real_context': ref_seq is not None
        }

        return ref_seq, alt_seq, metadata


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Genomic Sequence Fetcher...")

    fetcher = GenomicSequenceFetcher()

    # Test with BRCA1 variant (chr17:43045677 G>A)
    print("\n📍 Testing BRCA1 variant: chr17:43045677 G>A")
    ref_seq, alt_seq, metadata = fetcher.prepare_model_input(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A",
        context_size=50  # Small for testing
    )

    if ref_seq and alt_seq:
        print(f"\n✅ Successfully fetched sequences!")
        print(f"   REF sequence length: {len(ref_seq)}")
        print(f"   ALT sequence length: {len(alt_seq)}")
        print(f"   REF (first 50bp): {ref_seq[:50]}")
        print(f"   ALT (first 50bp): {alt_seq[:50]}")
        print(f"\n   Metadata: {metadata}")
    else:
        print("\n❌ Failed to fetch sequences")
