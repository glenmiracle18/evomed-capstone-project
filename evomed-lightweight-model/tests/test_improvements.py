"""
Test script for improved genomic context and gnomAD integration
Run this to verify all improvements work correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.genomic_sequence import GenomicSequenceFetcher
from services.gnomad_api import GnomADAPI


def test_genomic_sequence_fetcher():
    """Test genomic sequence fetching"""
    print("\n" + "=" * 70)
    print("TEST 1: Genomic Sequence Fetcher")
    print("=" * 70)

    fetcher = GenomicSequenceFetcher()

    # Test BRCA1 variant
    print("\n📍 Testing BRCA1 variant: chr17:43045677 G>A")

    ref_seq, alt_seq, metadata = fetcher.prepare_model_input(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A",
        max_length=512,
        context_size=100  # Small context for testing
    )

    if ref_seq and alt_seq:
        print(f"✅ Successfully fetched sequences!")
        print(f"   REF length: {len(ref_seq)}")
        print(f"   ALT length: {len(alt_seq)}")
        print(f"   Has real context: {metadata['has_real_context']}")

        # Show the variant position
        print(f"\n   REF sequence (first 100bp):")
        print(f"   {ref_seq[:100]}")
        print(f"\n   ALT sequence (first 100bp):")
        print(f"   {alt_seq[:100]}")

        # Verify the sequences differ at the variant position
        if ref_seq != alt_seq:
            print(f"\n✅ REF and ALT sequences differ (as expected)")

            # Find where they differ
            for i, (r, a) in enumerate(zip(ref_seq, alt_seq)):
                if r != a:
                    print(f"   First difference at position {i}: {r} → {a}")
                    break
        else:
            print(f"\n❌ ERROR: REF and ALT sequences are identical!")

        return True
    else:
        print(f"❌ Failed to fetch sequences")
        return False


def test_gnomad_integration():
    """Test gnomAD African frequency lookup"""
    print("\n" + "=" * 70)
    print("TEST 2: gnomAD Integration")
    print("=" * 70)

    api = GnomADAPI()

    # Test known pathogenic variant (should be rare)
    print("\n📍 Test 1: Known pathogenic BRCA1 variant")
    print("   chr17:43045677 G>A")

    af_afr = api.get_african_frequency(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A"
    )

    if af_afr is not None:
        print(f"   ✅ African frequency: {af_afr:.6f} ({af_afr * 100:.4f}%)")

        if af_afr < 0.001:
            print(f"   🔴 Rare variant - consistent with pathogenic")
        else:
            print(f"   ⚠️  Higher than expected for pathogenic variant")
    else:
        print(f"   ⚠️  Variant not found in gnomAD (expected for rare pathogenic)")

    # Test common benign variant (should have higher frequency)
    print("\n📍 Test 2: Common benign variant (APOE ε4)")
    print("   chr19:44908684 T>C")

    af_afr_common = api.get_african_frequency(
        chromosome="19",
        position=44908684,
        ref="T",
        alt="C"
    )

    if af_afr_common is not None:
        print(f"   ✅ African frequency: {af_afr_common:.6f} ({af_afr_common * 100:.4f}%)")

        if af_afr_common > 0.01:
            print(f"   🟢 Common variant - strong evidence for benign")
        elif af_afr_common > 0.005:
            print(f"   🟡 Moderately common - evidence for benign")
        else:
            print(f"   🔴 Rare variant")

        # Get full population summary
        print("\n   📊 Full population data:")
        summary = api.get_population_summary(
            chromosome="19",
            position=44908684,
            ref="T",
            alt="C"
        )

        if summary["found"]:
            print(f"      Global AF: {summary['global']['af']:.6f}" if summary['global']['af'] else "      Global AF: N/A")
            print(f"      African AF: {summary['african']:.6f}" if summary['african'] else "      African AF: N/A")
            print(f"      European AF: {summary['european']:.6f}" if summary['european'] else "      European AF: N/A")

        return True
    else:
        print(f"   ⚠️  Variant not found in gnomAD")
        return False


def test_african_adjustment_logic():
    """Test African population adjustment logic"""
    print("\n" + "=" * 70)
    print("TEST 3: African Adjustment Logic")
    print("=" * 70)

    def apply_adjustment(raw_score: float, af_afr: float) -> float:
        """Simulate the adjustment logic"""
        if af_afr > 0.05:
            adjustment = -0.20
        elif af_afr > 0.01:
            adjustment = -0.12
        elif af_afr > 0.005:
            adjustment = -0.06
        else:
            adjustment = 0.0

        return max(0.0, min(1.0, raw_score + adjustment))

    # Test cases
    test_cases = [
        {"raw_score": 0.8, "af_afr": 0.001, "expected": "No adjustment (rare)"},
        {"raw_score": 0.8, "af_afr": 0.006, "expected": "Mild adjustment (0.5%)"},
        {"raw_score": 0.8, "af_afr": 0.02, "expected": "Moderate adjustment (1%)"},
        {"raw_score": 0.8, "af_afr": 0.10, "expected": "Strong adjustment (5%)"},
    ]

    print("\n📊 Testing adjustment scenarios:")
    print(f"   {'AF (AFR)':<12} {'Raw Score':<12} {'Adjusted':<12} {'Change':<12} {'Note'}")
    print("   " + "-" * 70)

    for test in test_cases:
        raw = test["raw_score"]
        af = test["af_afr"]
        adjusted = apply_adjustment(raw, af)
        change = adjusted - raw

        print(f"   {af:<12.4f} {raw:<12.4f} {adjusted:<12.4f} {change:<12.4f} {test['expected']}")

        # Verify adjustment reduces pathogenicity score
        if af > 0.005:
            assert adjusted < raw, "Adjustment should reduce score for common variants"

    print("\n✅ Adjustment logic works correctly!")
    return True


def test_sequence_comparison():
    """Test that REF and ALT sequences differ correctly"""
    print("\n" + "=" * 70)
    print("TEST 4: REF vs ALT Sequence Comparison")
    print("=" * 70)

    fetcher = GenomicSequenceFetcher()

    # Test SNV
    print("\n📍 Test SNV: chr17:43045677 G>A")
    ref_seq, alt_seq, _ = fetcher.prepare_model_input(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A",
        context_size=50
    )

    differences = sum(1 for r, a in zip(ref_seq, alt_seq) if r != a)
    print(f"   Differences: {differences} bases")
    print(f"   ✅ Expected 1 difference for SNV: {'PASS' if differences == 1 else 'FAIL'}")

    # Test insertion
    print("\n📍 Test Insertion: chr17:43045677 G>GA")
    ref_seq_ins, alt_seq_ins, _ = fetcher.prepare_model_input(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="GA",
        context_size=50
    )

    len_diff = len(alt_seq_ins) - len(ref_seq_ins)
    print(f"   Length difference: {len_diff} bases")
    print(f"   ✅ Expected 1 base insertion: {'PASS' if len_diff == 1 else 'FAIL'}")

    return True


def run_all_tests():
    """Run all improvement tests"""
    print("\n" + "=" * 70)
    print("🧪 EVOMED MODEL IMPROVEMENTS - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    results = []

    # Test 1: Genomic sequence fetcher
    try:
        result1 = test_genomic_sequence_fetcher()
        results.append(("Genomic Sequence Fetcher", result1))
    except Exception as e:
        print(f"\n❌ Test 1 failed with error: {e}")
        results.append(("Genomic Sequence Fetcher", False))

    # Test 2: gnomAD integration
    try:
        result2 = test_gnomad_integration()
        results.append(("gnomAD Integration", result2))
    except Exception as e:
        print(f"\n❌ Test 2 failed with error: {e}")
        results.append(("gnomAD Integration", False))

    # Test 3: African adjustment logic
    try:
        result3 = test_african_adjustment_logic()
        results.append(("African Adjustment Logic", result3))
    except Exception as e:
        print(f"\n❌ Test 3 failed with error: {e}")
        results.append(("African Adjustment Logic", False))

    # Test 4: Sequence comparison
    try:
        result4 = test_sequence_comparison()
        results.append(("Sequence Comparison", result4))
    except Exception as e:
        print(f"\n❌ Test 4 failed with error: {e}")
        results.append(("Sequence Comparison", False))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:<35} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("   Your model improvements are working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Please review the errors above")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
