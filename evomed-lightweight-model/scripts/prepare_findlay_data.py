"""
Prepare training data from Findlay et al. 2018 BRCA1 saturation mutagenesis dataset
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from configs.config import DATA_DIR, RANDOM_SEED, TEST_SPLIT, TRAIN_SPLIT, VAL_SPLIT

# Set random seed
np.random.seed(RANDOM_SEED)


def main():
    """Main data preparation pipeline"""
    print("=" * 60)
    print("EvoMed Lightweight Model - BRCA1 Data Preparation")
    print("=" * 60)

    # Load dataset
    print("\n📂 Loading BRCA1 saturation mutagenesis dataset...")
    dataset_path = DATA_DIR / "41586_2018_461_MOESM3_ESM.xlsx"

    if not dataset_path.exists():
        print(f"   ❌ Dataset not found: {dataset_path}")
        return 1

    # Load Excel file (header is on row 2)
    df = pd.read_excel(dataset_path, header=2)
    print(f"   ✅ Loaded {len(df):,} variants from Findlay et al. 2018")

    # Clean and standardize columns
    df = df[
        [
            "chromosome",
            "position (hg19)",
            "reference",
            "alt",
            "function.score.mean",
            "func.class",
        ]
    ].copy()

    df.rename(
        columns={
            "chromosome": "chromosome",
            "position (hg19)": "position",
            "reference": "ref",
            "function.score.mean": "func_score",
            "func.class": "func_class",
        },
        inplace=True,
    )

    # Show class distribution
    print(f"\n📊 Functional class distribution:")
    class_counts = df["func_class"].value_counts()
    for cls, count in class_counts.items():
        print(f"   {cls}: {count:,} ({count / len(df) * 100:.1f}%)")

    # Convert to binary labels
    # LOF (Loss of Function) = Pathogenic (1)
    # FUNC/INT (Functional/Intermediate) = Benign (0)
    def func_class_to_label(fc):
        if pd.isna(fc):
            return -1
        fc_str = str(fc).upper()
        if "LOF" in fc_str:
            return 1  # Pathogenic
        elif "FUNC" in fc_str or "INT" in fc_str:
            return 0  # Benign
        else:
            return -1

    df["label"] = df["func_class"].apply(func_class_to_label)

    # Filter out uncertain variants
    before = len(df)
    df = df[df["label"] != -1]
    after = len(df)
    print(
        f"\n🔄 Filtered uncertain variants: {before:,} → {after:,} ({before - after:,} removed)"
    )

    # Distribution after filtering
    pathogenic = (df["label"] == 1).sum()
    benign = (df["label"] == 0).sum()
    print(f"\n📈 Label distribution:")
    print(f"   Pathogenic (LOF): {pathogenic:,} ({pathogenic / len(df) * 100:.1f}%)")
    print(f"   Benign (FUNC): {benign:,} ({benign / len(df) * 100:.1f}%)")

    # Split dataset
    print("\n✂️  Splitting dataset...")
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    n = len(df)
    train_end = int(n * TRAIN_SPLIT)
    val_end = train_end + int(n * VAL_SPLIT)

    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]

    print(f"   Train: {len(train_df):,} variants")
    print(f"   Val:   {len(val_df):,} variants")
    print(f"   Test:  {len(test_df):,} variants")

    # Save datasets
    print("\n💾 Saving datasets...")
    output_dir = DATA_DIR / "processed"
    output_dir.mkdir(exist_ok=True, parents=True)

    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "val.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)

    print(f"   ✅ train.csv: {len(train_df):,} variants")
    print(f"   ✅ val.csv: {len(val_df):,} variants")
    print(f"   ✅ test.csv: {len(test_df):,} variants")

    # Save metadata
    metadata = {
        "total_variants": len(df),
        "train_size": len(train_df),
        "val_size": len(val_df),
        "test_size": len(test_df),
        "pathogenic_count": int(pathogenic),
        "benign_count": int(benign),
        "random_seed": RANDOM_SEED,
        "dataset": "Findlay et al. 2018 BRCA1 saturation mutagenesis",
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ metadata.json")

    print("\n" + "=" * 60)
    print("✅ Data preparation complete!")
    print("=" * 60)
    print(f"\nDatasets saved to: {output_dir}")
    print(f"\n📋 Next steps:")
    print(f"   1. Set HuggingFace token: export HF_TOKEN='your_token'")
    print(f"   2. Start training: modal run training/train_modal.py")

    return 0


if __name__ == "__main__":
    exit(main())
