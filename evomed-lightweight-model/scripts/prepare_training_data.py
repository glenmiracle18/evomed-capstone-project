"""
Prepare training data from BRCA Exchange and ClinVar datasets
Includes African population frequency integration
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import json
from tqdm import tqdm
import requests

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from configs.config import (
    DATA_DIR, TARGET_GENE, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT,
    RANDOM_SEED, GENOMIC_CONTEXT_WINDOW
)

# Set random seed
np.random.seed(RANDOM_SEED)

def load_datasets():
    """Load BRCA Exchange and ClinVar datasets"""
    print("\n📂 Loading datasets...")

    brca_exchange_path = DATA_DIR / "brca_exchange_brca1.tsv"
    clinvar_path = DATA_DIR / "clinvar_brca1.txt"

    dfs = {}

    if brca_exchange_path.exists():
        dfs['brca_exchange'] = pd.read_csv(brca_exchange_path, sep='\t', low_memory=False)
        print(f"   BRCA Exchange: {len(dfs['brca_exchange']):,} variants")
    else:
        print(f"   ⚠️  BRCA Exchange file not found: {brca_exchange_path}")

    if clinvar_path.exists():
        dfs['clinvar'] = pd.read_csv(clinvar_path, sep='\t', low_memory=False)
        print(f"   ClinVar: {len(dfs['clinvar']):,} variants")
    else:
        print(f"   ⚠️  ClinVar file not found: {clinvar_path}")

    return dfs

def parse_clinical_significance(sig_str: str) -> int:
    """
    Parse clinical significance to binary label
    Returns:
        1 = Pathogenic/Likely Pathogenic
        0 = Benign/Likely Benign
        -1 = Uncertain/Conflicting (will be filtered out)
    """
    if pd.isna(sig_str):
        return -1

    sig_str = str(sig_str).lower()

    # Pathogenic
    if 'pathogenic' in sig_str and 'benign' not in sig_str:
        return 1

    # Benign
    if 'benign' in sig_str and 'pathogenic' not in sig_str:
        return 0

    # Everything else (VUS, conflicting, etc.)
    return -1

def process_brca_exchange(df: pd.DataFrame) -> pd.DataFrame:
    """Process BRCA Exchange dataset"""
    print("\n🔄 Processing BRCA Exchange data...")

    # Key columns
    processed = pd.DataFrame()

    # Basic variant info
    processed['chromosome'] = df.get('Chr', df.get('Chromosome'))
    processed['position'] = df.get('Pos', df.get('Genomic_Coordinate_hg38'))
    processed['ref'] = df.get('Ref', df.get('Reference_Sequence'))
    processed['alt'] = df.get('Alt', df.get('Alternate_Sequence'))

    # Clinical significance
    if 'Clinical_Significance_ENIGMA' in df.columns:
        processed['label'] = df['Clinical_Significance_ENIGMA'].apply(parse_clinical_significance)
    elif 'Pathogenicity_expert' in df.columns:
        processed['label'] = df['Pathogenicity_expert'].apply(parse_clinical_significance)
    else:
        print("   ⚠️  No clinical significance column found")
        processed['label'] = -1

    # Population frequencies (if available)
    if 'Allele_Frequency_AFR' in df.columns:
        processed['af_afr'] = pd.to_numeric(df['Allele_Frequency_AFR'], errors='coerce')
    else:
        processed['af_afr'] = np.nan

    # Source
    processed['source'] = 'brca_exchange'

    # Filter out uncertain variants
    before = len(processed)
    processed = processed[processed['label'] != -1]
    after = len(processed)
    print(f"   Filtered: {before:,} → {after:,} variants ({before - after:,} uncertain removed)")

    # Distribution
    if len(processed) > 0:
        pathogenic = (processed['label'] == 1).sum()
        benign = (processed['label'] == 0).sum()
        print(f"   Pathogenic: {pathogenic:,} ({pathogenic/len(processed)*100:.1f}%)")
        print(f"   Benign: {benign:,} ({benign/len(processed)*100:.1f}%)")

    return processed

def process_clinvar(df: pd.DataFrame) -> pd.DataFrame:
    """Process ClinVar dataset"""
    print("\n🔄 Processing ClinVar data...")

    processed = pd.DataFrame()

    # Basic variant info
    processed['chromosome'] = df['Chromosome']
    processed['position'] = df['Start']
    processed['ref'] = df['ReferenceAllele']
    processed['alt'] = df['AlternateAllele']

    # Clinical significance
    processed['label'] = df['ClinicalSignificance'].apply(parse_clinical_significance)

    # Review status (for quality filtering)
    processed['review_status'] = df.get('ReviewStatus', '')

    # Source
    processed['source'] = 'clinvar'

    # Population frequency (not directly in ClinVar, will get from gnomAD)
    processed['af_afr'] = np.nan

    # Quality filter: keep only high-quality submissions
    quality_keywords = ['practice guideline', 'reviewed by expert', 'criteria provided']
    mask = processed['review_status'].str.lower().str.contains('|'.join(quality_keywords), na=False)

    before = len(processed)
    processed = processed[mask | (processed['label'] != -1)]
    after = len(processed)

    # Filter out uncertain variants
    before = len(processed)
    processed = processed[processed['label'] != -1]
    after = len(processed)
    print(f"   Filtered: {before:,} → {after:,} variants ({before - after:,} uncertain removed)")

    # Distribution
    if len(processed) > 0:
        pathogenic = (processed['label'] == 1).sum()
        benign = (processed['label'] == 0).sum()
        print(f"   Pathogenic: {pathogenic:,} ({pathogenic/len(processed)*100:.1f}%)")
        print(f"   Benign: {benign:,} ({benign/len(processed)*100:.1f}%)")

    return processed.drop(columns=['review_status'])

def merge_datasets(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge and deduplicate datasets"""
    print("\n🔗 Merging datasets...")

    all_variants = []

    if 'brca_exchange' in dfs:
        all_variants.append(dfs['brca_exchange'])

    if 'clinvar' in dfs:
        all_variants.append(dfs['clinvar'])

    if not all_variants:
        raise ValueError("No valid datasets to merge!")

    # Combine
    merged = pd.concat(all_variants, ignore_index=True)
    print(f"   Combined: {len(merged):,} variants")

    # Deduplicate by position and alt allele
    before = len(merged)
    merged = merged.drop_duplicates(subset=['chromosome', 'position', 'alt'], keep='first')
    after = len(merged)
    print(f"   Deduplicated: {before:,} → {after:,} variants ({before - after:,} duplicates removed)")

    # Remove rows with missing critical info
    before = len(merged)
    merged = merged.dropna(subset=['chromosome', 'position', 'alt'])
    after = len(merged)
    if before != after:
        print(f"   Removed missing data: {before - after:,} variants")

    return merged

def create_sequence_context(row: pd.Series, reference_seq: str = None) -> str:
    """
    Create genomic context around variant
    For now, we'll use a simple approach of creating the sequence context
    In production, you'd fetch this from Ensembl or a reference genome
    """
    # This is a placeholder - in real implementation, we'd:
    # 1. Fetch the reference sequence around the variant position
    # 2. Apply the variant to create the alternate sequence
    # 3. Return the context window

    # For now, return a simple representation
    # The training script will handle actual sequence fetching
    ref = str(row['ref'])
    alt = str(row['alt'])

    # Create a dummy sequence (will be replaced with actual sequence in training)
    return f"ref:{ref}|alt:{alt}|pos:{row['position']}"

def split_dataset(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Split dataset into train/val/test"""
    print("\n✂️  Splitting dataset...")

    # Shuffle
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Calculate split indices
    n = len(df)
    train_end = int(n * TRAIN_SPLIT)
    val_end = train_end + int(n * VAL_SPLIT)

    splits = {
        'train': df[:train_end],
        'val': df[train_end:val_end],
        'test': df[val_end:],
    }

    for split_name, split_df in splits.items():
        pathogenic = (split_df['label'] == 1).sum()
        benign = (split_df['label'] == 0).sum()
        total = len(split_df)
        print(f"   {split_name.capitalize():5} {total:,} variants "
              f"(Pathogenic: {pathogenic:,}, Benign: {benign:,})")

    return splits

def save_datasets(splits: Dict[str, pd.DataFrame]):
    """Save processed datasets"""
    print("\n💾 Saving datasets...")

    output_dir = DATA_DIR / "processed"
    output_dir.mkdir(exist_ok=True)

    for split_name, df in splits.items():
        output_path = output_dir / f"{split_name}.csv"
        df.to_csv(output_path, index=False)
        print(f"   ✅ {split_name}: {output_path} ({len(df):,} variants)")

    # Also save combined dataset
    combined = pd.concat([splits['train'], splits['val'], splits['test']])
    combined_path = output_dir / "all_variants.csv"
    combined.to_csv(combined_path, index=False)
    print(f"   ✅ combined: {combined_path} ({len(combined):,} variants)")

    # Save metadata
    metadata = {
        'total_variants': len(combined),
        'train_size': len(splits['train']),
        'val_size': len(splits['val']),
        'test_size': len(splits['test']),
        'pathogenic_count': int((combined['label'] == 1).sum()),
        'benign_count': int((combined['label'] == 0).sum()),
        'random_seed': RANDOM_SEED,
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ metadata: {metadata_path}")

def main():
    """Main data preparation pipeline"""
    print("=" * 60)
    print("EvoMed Lightweight Model - Data Preparation")
    print("=" * 60)

    # Load raw datasets
    raw_dfs = load_datasets()

    if not raw_dfs:
        print("\n❌ No datasets found! Please run download_data.py first.")
        return 1

    # Process each dataset
    processed_dfs = {}

    if 'brca_exchange' in raw_dfs:
        processed_dfs['brca_exchange'] = process_brca_exchange(raw_dfs['brca_exchange'])

    if 'clinvar' in raw_dfs:
        processed_dfs['clinvar'] = process_clinvar(raw_dfs['clinvar'])

    # Merge datasets
    merged = merge_datasets(processed_dfs)

    # Check if we have enough data
    if len(merged) < 100:
        print(f"\n⚠️  Warning: Only {len(merged)} variants found. Need at least 100 for training.")
        print("   Proceeding anyway, but results may be poor.")

    # Split dataset
    splits = split_dataset(merged)

    # Save datasets
    save_datasets(splits)

    # Summary
    print("\n" + "=" * 60)
    print("✅ Data preparation complete!")
    print("=" * 60)
    print(f"\nDatasets saved to: {DATA_DIR / 'processed'}")
    print("\n📋 Next steps:")
    print("   1. Review the data: cat data/processed/metadata.json")
    print("   2. Start training: modal run training/train_modal.py")

    return 0

if __name__ == "__main__":
    exit(main())
