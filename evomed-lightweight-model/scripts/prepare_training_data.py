"""
Prepare training data from BRCA Exchange dataset
Includes African population frequency integration and ACMG/AMP adjustments
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from configs.config import (
    DATA_DIR,
    RANDOM_SEED,
    TEST_SPLIT,
    TRAIN_SPLIT,
    VAL_SPLIT,
)

# Set random seed
np.random.seed(RANDOM_SEED)


def load_brca_exchange_data():
    """Load BRCA1 variants from BRCA Exchange TSV file"""
    print("\n📂 Loading BRCA Exchange data...")

    # Use the full variants file (297MB)
    brca_file = DATA_DIR / "variants(1).tsv"

    if not brca_file.exists():
        print(f"   ❌ File not found: {brca_file}")
        print("   Please download data first!")
        return None

    try:
        # Load full dataset
        print(f"   Loading {brca_file.name} (this may take a moment)...")
        df = pd.read_csv(brca_file, sep="\t", low_memory=False)
        print(f"   ✅ Loaded {len(df):,} total variants")

        # Filter for BRCA1 only
        brca1_df = df[df["Gene_Symbol"] == "BRCA1"].copy()
        print(f"   ✅ Filtered to {len(brca1_df):,} BRCA1 variants")

        return brca1_df
    except Exception as e:
        print(f"   ❌ Error loading {brca_file}: {e}")
        return None


def parse_clinical_significance(row: pd.Series) -> int:
    """
    Parse clinical significance to binary label
    Priority: ENIGMA > ClinVar > Pathogenicity_expert

    Returns:
        1 = Pathogenic/Likely Pathogenic
        0 = Benign/Likely Benign
        -1 = Uncertain/Conflicting/VUS (will be filtered out)
    """
    # Priority 1: ENIGMA (most authoritative)
    enigma_sig = row.get("Clinical_significance_ENIGMA", None)
    if pd.notna(enigma_sig):
        sig_str = str(enigma_sig).lower()
        if "pathogenic" in sig_str and "benign" not in sig_str:
            return 1
        if "benign" in sig_str and "pathogenic" not in sig_str:
            return 0

    # Priority 2: ClinVar
    clinvar_sig = row.get("Clinical_Significance_ClinVar", None)
    if pd.notna(clinvar_sig):
        sig_str = str(clinvar_sig).lower()
        if "pathogenic" in sig_str and "benign" not in sig_str:
            return 1
        if "benign" in sig_str and "pathogenic" not in sig_str:
            return 0

    # Priority 3: Expert pathogenicity
    expert_sig = row.get("Pathogenicity_expert", None)
    if pd.notna(expert_sig):
        sig_str = str(expert_sig).lower()
        if "pathogenic" in sig_str and "benign" not in sig_str:
            return 1
        if "benign" in sig_str and "pathogenic" not in sig_str:
            return 0

    # Everything else (VUS, conflicting, etc.)
    return -1


def extract_african_frequency(row: pd.Series) -> float:
    """
    Extract African/African American allele frequency
    Priority: gnomAD v4 genome > gnomAD v4 exome > gnomAD v2/v3 > ExAC > 1000 Genomes
    """
    # Try gnomAD v4 genome (most recent)
    af_afr = row.get("Allele_frequency_genome_AFR_GnomAD", None)
    if pd.notna(af_afr):
        try:
            af_val = float(af_afr)
            if af_val > 0:
                return af_val
        except (ValueError, TypeError):
            pass

    # Try gnomAD v4 exome
    af_afr = row.get("Allele_frequency_exome_AFR_GnomAD", None)
    if pd.notna(af_afr):
        try:
            af_val = float(af_afr)
            if af_val > 0:
                return af_val
        except (ValueError, TypeError):
            pass

    # Try gnomAD v3 genome
    af_afr = row.get("Allele_frequency_genome_AFR_GnomADv3", None)
    if pd.notna(af_afr):
        try:
            af_val = float(af_afr)
            if af_val > 0:
                return af_val
        except (ValueError, TypeError):
            pass

    # Try ExAC
    af_afr = row.get("Allele_frequency_AFR_ExAC", None)
    if pd.notna(af_afr):
        try:
            af_val = float(af_afr)
            if af_val > 0:
                return af_val
        except (ValueError, TypeError):
            pass

    # Try 1000 Genomes
    af_afr = row.get("AFR_Allele_frequency_1000_Genomes", None)
    if pd.notna(af_afr):
        try:
            af_val = float(af_afr)
            if af_val > 0:
                return af_val
        except (ValueError, TypeError):
            pass

    # No African frequency data available
    return 0.0


def apply_african_adjustment(label: int, af_afr: float) -> Tuple[int, str]:
    """
    Apply ACMG/AMP frequency-based adjustment to labels

    BA1 criterion: Allele frequency > 5% in any population = Stand-alone Benign
    This is applied DURING TRAINING to correct likely misclassifications

    Returns:
        (adjusted_label, reason)
    """
    if af_afr > 0.05 and label == 1:  # BA1 criterion
        return (
            0,
            f"BA1: High AFR frequency ({af_afr:.3f} > 0.05) - relabeled Pathogenic→Benign",
        )

    return label, "No adjustment"


def process_brca_exchange_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Process BRCA Exchange dataset with proper column mapping"""
    print("\n🔄 Processing BRCA Exchange dataset...")

    processed_data = []
    adjustments_made = 0

    print("   Parsing variants...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="   Processing"):
        # Parse clinical significance
        label = parse_clinical_significance(row)

        # Skip VUS and uncertain
        if label == -1:
            continue

        # Extract African frequency
        af_afr = extract_african_frequency(row)

        # Apply African adjustment (BA1 criterion)
        original_label = label
        label, adjustment_reason = apply_african_adjustment(label, af_afr)
        if original_label != label:
            adjustments_made += 1

        # Extract variant information
        variant_data = {
            "chromosome": row.get("Chr", "chr17"),
            "position": row.get("Pos", 0),
            "ref": row.get("Ref", ""),
            "alt": row.get("Alt", ""),
            "label": label,
            "original_label": original_label,
            "af_afr": af_afr,
            "adjustment_reason": adjustment_reason,
            "hgvs_cdna": row.get("HGVS_cDNA", ""),
            "hgvs_protein": row.get("HGVS_Protein", ""),
            "source_enigma": 1
            if pd.notna(row.get("Clinical_significance_ENIGMA"))
            else 0,
            "source_clinvar": 1
            if pd.notna(row.get("Clinical_Significance_ClinVar"))
            else 0,
        }

        processed_data.append(variant_data)

    # Create DataFrame
    processed_df = pd.DataFrame(processed_data)

    print(f"\n   📊 Processing Summary:")
    print(f"   Total variants processed: {len(df):,}")
    print(f"   Labeled variants: {len(processed_df):,}")
    print(f"   Unlabeled/VUS filtered: {len(df) - len(processed_df):,}")
    print(f"   African frequency adjustments: {adjustments_made:,}")

    if len(processed_df) > 0:
        pathogenic = (processed_df["label"] == 1).sum()
        benign = (processed_df["label"] == 0).sum()
        with_afr_freq = (processed_df["af_afr"] > 0).sum()

        print(f"\n   📈 Label Distribution:")
        print(
            f"   Pathogenic: {pathogenic:,} ({pathogenic / len(processed_df) * 100:.1f}%)"
        )
        print(f"   Benign: {benign:,} ({benign / len(processed_df) * 100:.1f}%)")
        print(f"   Class Imbalance Ratio: {pathogenic / benign:.2f}:1")

        print(f"\n   🌍 African Frequency Coverage:")
        print(
            f"   Variants with AFR frequency > 0: {with_afr_freq:,} ({with_afr_freq / len(processed_df) * 100:.1f}%)"
        )
        print(
            f"   Variants with AFR frequency > 1%: {(processed_df['af_afr'] > 0.01).sum():,}"
        )
        print(
            f"   Variants with AFR frequency > 5%: {(processed_df['af_afr'] > 0.05).sum():,}"
        )

    return processed_df


def split_dataset(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Split dataset into train/val/test with stratification"""
    print("\n✂️  Splitting dataset (stratified)...")

    # First split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df,
        test_size=(VAL_SPLIT + TEST_SPLIT),
        random_state=RANDOM_SEED,
        stratify=df["label"],  # Maintain class balance
    )

    # Second split: val vs test
    val_size_adjusted = VAL_SPLIT / (VAL_SPLIT + TEST_SPLIT)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_size_adjusted),
        random_state=RANDOM_SEED,
        stratify=temp_df["label"],
    )

    splits = {
        "train": train_df,
        "val": val_df,
        "test": test_df,
    }

    print(f"\n   Split sizes:")
    for split_name, split_df in splits.items():
        pathogenic = (split_df["label"] == 1).sum()
        benign = (split_df["label"] == 0).sum()
        total = len(split_df)
        print(
            f"   {split_name.capitalize():5} {total:,} variants "
            f"(P: {pathogenic:,} [{pathogenic / total * 100:.1f}%], "
            f"B: {benign:,} [{benign / total * 100:.1f}%])"
        )

    return splits


def save_datasets(splits: Dict[str, pd.DataFrame]):
    """Save processed datasets"""
    print("\n💾 Saving datasets...")

    output_dir = DATA_DIR / "processed"
    output_dir.mkdir(exist_ok=True)

    for split_name, df in splits.items():
        output_path = output_dir / f"{split_name}.csv"
        df.to_csv(output_path, index=False)
        print(f"   ✅ {split_name:5} {output_path} ({len(df):,} variants)")

    # Save combined dataset
    combined = pd.concat([splits["train"], splits["val"], splits["test"]])
    combined_path = output_dir / "all_variants.csv"
    combined.to_csv(combined_path, index=False)
    print(f"   ✅ {'all':5} {combined_path} ({len(combined):,} variants)")

    # Calculate metadata
    pathogenic_count = int((combined["label"] == 1).sum())
    benign_count = int((combined["label"] == 0).sum())
    adjustments_made = int((combined["label"] != combined["original_label"]).sum())

    metadata = {
        "total_variants": len(combined),
        "train_size": len(splits["train"]),
        "val_size": len(splits["val"]),
        "test_size": len(splits["test"]),
        "pathogenic_count": pathogenic_count,
        "benign_count": benign_count,
        "class_imbalance_ratio": round(pathogenic_count / benign_count, 2),
        "african_frequency_adjustments": adjustments_made,
        "variants_with_afr_frequency": int((combined["af_afr"] > 0).sum()),
        "variants_with_afr_freq_gt_1pct": int((combined["af_afr"] > 0.01).sum()),
        "variants_with_afr_freq_gt_5pct": int((combined["af_afr"] > 0.05).sum()),
        "random_seed": RANDOM_SEED,
        "train_split": TRAIN_SPLIT,
        "val_split": VAL_SPLIT,
        "test_split": TEST_SPLIT,
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ {'meta':5} {metadata_path}")


def main():
    """Main data preparation pipeline"""
    print("=" * 70)
    print("EvoMed - BRCA1 Variant Analysis Data Preparation")
    print("=" * 70)

    # Load raw dataset
    raw_df = load_brca_exchange_data()

    if raw_df is None or len(raw_df) == 0:
        print("\n❌ No data found! Please check data files.")
        return 1

    # Process dataset
    processed_df = process_brca_exchange_dataset(raw_df)

    # Check if we have enough data
    if len(processed_df) < 100:
        print(f"\n⚠️  Warning: Only {len(processed_df)} labeled variants found.")
        print("   Need at least 100 for meaningful training.")
        print("   This may indicate a problem with the data or labeling criteria.")
        return 1

    # Split dataset
    splits = split_dataset(processed_df)

    # Save datasets
    save_datasets(splits)

    # Summary
    print("\n" + "=" * 70)
    print("✅ Data preparation complete!")
    print("=" * 70)
    print(f"\nDatasets saved to: {DATA_DIR / 'processed'}")

    # Show example variants
    print("\n📋 Example variants (first 3 from training set):")
    example_df = splits["train"].head(3)[
        ["chromosome", "position", "ref", "alt", "label", "af_afr", "hgvs_cdna"]
    ]
    print(example_df.to_string(index=False))

    print("\n📋 Next steps:")
    print("   1. Review the data: cat data/processed/metadata.json")
    print("   2. Check data quality: python scripts/verify_setup.py")
    print("   3. Start training: modal run training/train_modal.py")

    return 0


if __name__ == "__main__":
    exit(main())
