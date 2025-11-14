"""
Test script for inference-based African population adjustments
Run this locally to verify the logic before deploying to Modal
"""

from population_service import (
    apply_inference_based_adjustment,
    calculate_population_adjustment,
)


def test_inference_adjustments():
    """Test various scenarios for inference-based adjustments"""

    print("=" * 80)
    print("Testing Inference-Based African Population Adjustments")
    print("=" * 80)

    # Test cases: (score, expected_strategy, description)
    test_cases = [
        # Your actual variant
        (-0.000200, "benign_boost", "BRD4 enhancer C>G (your variant)"),
        # Borderline pathogenic
        (-0.0015, "borderline", "Borderline pathogenic variant"),
        (-0.0020, "borderline", "Borderline pathogenic (near edge)"),
        # Strong pathogenic
        (-0.0040, "strong_pathogenic", "Strong pathogenic variant"),
        # Clearly benign
        (0.0010, "benign_boost", "Clearly benign variant"),
        # Right at threshold
        (-0.0009178519, "benign_boost", "Exactly at threshold (benign side)"),
    ]

    for score, expected_strategy, description in test_cases:
        print(f"\n{'-' * 80}")
        print(f"Test: {description}")
        print(f"Original Evo2 Score: {score:.6f}")

        # Test without global frequency
        adjusted, adjustment, reasoning = apply_inference_based_adjustment(score)
        print(f"\nWithout global frequency:")
        print(f"  Adjusted Score: {adjusted:.6f}")
        print(f"  Adjustment: {adjustment:+.6f}")
        print(f"  Reasoning: {reasoning}")

        # Test with global frequency
        adjusted_with_global, adjustment_with_global, reasoning_with_global = (
            apply_inference_based_adjustment(score, global_af=0.0015)
        )
        print(f"\nWith global AF=0.0015 (0.15%):")
        print(f"  Adjusted Score: {adjusted_with_global:.6f}")
        print(f"  Adjustment: {adjustment_with_global:+.6f}")
        print(f"  Reasoning: {reasoning_with_global}")

    print("\n" + "=" * 80)
    print("Testing calculate_population_adjustment with error cases")
    print("=" * 80)

    # Test with error in freq_data (simulating gnomAD "Variant not found")
    error_freq_data = {
        "african_af": None,
        "global_af": None,
        "cached": False,
        "source": None,
        "error": "Failed to fetch from gnomAD",
    }

    print(f"\nTest: gnomAD returns 'Variant not found'")
    print(f"freq_data: {error_freq_data}")

    score = -0.000200  # Your variant
    adjusted, adjustment, reasoning = calculate_population_adjustment(
        score, error_freq_data, use_african_adjustment=True
    )

    print(f"\nOriginal Score: {score:.6f}")
    print(f"Adjusted Score: {adjusted:.6f}")
    print(f"Adjustment: {adjustment:+.6f}")
    print(f"Reasoning: {reasoning}")

    # Verify the adjustment was applied
    if adjustment > 0:
        print("\n✅ SUCCESS: Adjustment was applied despite gnomAD error!")
    else:
        print("\n❌ FAILED: No adjustment applied!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_inference_adjustments()
