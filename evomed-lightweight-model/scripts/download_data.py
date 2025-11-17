"""
Download BRCA1 variant datasets from BRCA Exchange and ClinVar
"""

import gzip
import shutil
import sys
from pathlib import Path

import requests
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from configs.config import BRCA_EXCHANGE_API_BASE, CLINVAR_FTP, DATA_DIR, TARGET_GENE


def download_file(url: str, output_path: Path, desc: str = "Downloading"):
    """Download a file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with (
            open(output_path, "wb") as f,
            tqdm(
                desc=desc,
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar,
        ):
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)

        print(f"✅ Downloaded: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return False


def download_brca_exchange():
    """
    Download BRCA Exchange dataset using the official API

    Uses the Search Index API endpoint with proper parameters:
    - format=tsv for tab-separated values
    - filter[]=Gene_Symbol&filterValue[]=BRCA1 to get only BRCA1 variants
    - include[]=all to include all data sources (ClinVar, ENIGMA, gnomAD, etc.)
    - page_size=0 to disable pagination and get all results
    """
    print("\n📥 Downloading BRCA Exchange dataset via API...")
    filtered_path = DATA_DIR / "brca_exchange_brca1.tsv"

    if filtered_path.exists():
        print(f"⚠️  File already exists: {filtered_path}")
        user_input = input("Re-download? (y/n): ")
        if user_input.lower() != "y":
            return True

    try:
        # Build API URL with correct parameters according to documentation
        # Format: /backend/data/?format=tsv&filter[]=Gene_Symbol&filterValue[]=BRCA1&include[]=all&page_size=0
        params = {
            "format": "tsv",
            "filter[]": "Gene_Symbol",
            "filterValue[]": TARGET_GENE,
            "include[]": "all",  # Include all data sources
            "page_size": "0",  # Disable pagination to get all results
        }

        print(f"   API endpoint: {BRCA_EXCHANGE_API_BASE}")
        print(f"   Filtering for gene: {TARGET_GENE}")
        print(f"   Including all data sources (ClinVar, ENIGMA, gnomAD, etc.)")

        # Make API request
        response = requests.get(BRCA_EXCHANGE_API_BASE, params=params, timeout=300)
        response.raise_for_status()

        # Save the TSV data
        with open(filtered_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Downloaded BRCA Exchange data via API")

        # Quick stats
        import pandas as pd

        df = pd.read_csv(filtered_path, sep="\t", low_memory=False)
        print(f"   Total {TARGET_GENE} variants: {len(df):,}")

        # Show available columns with population data
        pop_cols = [
            col
            for col in df.columns
            if "gnomAD" in col or "ExAC" in col or "1000" in col or "AF" in col
        ]
        if pop_cols:
            print(f"   Population frequency columns available: {len(pop_cols)}")
            print(f"   Examples: {', '.join(pop_cols[:5])}")

        # Check for African population data
        african_cols = [
            col
            for col in df.columns
            if "afr" in col.lower() or "african" in col.lower()
        ]
        if african_cols:
            print(f"   African population data columns: {', '.join(african_cols[:3])}")

        return True

    except requests.exceptions.Timeout:
        print(f"❌ API request timed out after 300 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading from BRCA Exchange API: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing BRCA Exchange data: {e}")
        return False


def download_clinvar():
    """Download ClinVar variant summary"""
    print("\n📥 Downloading ClinVar dataset...")
    output_path_gz = DATA_DIR / "clinvar_variant_summary.txt.gz"
    output_path = DATA_DIR / "clinvar_variant_summary.txt"

    if output_path.exists():
        print(f"⚠️  File already exists: {output_path}")
        user_input = input("Re-download? (y/n): ")
        if user_input.lower() != "y":
            return True

    # Download gzipped file
    success = download_file(CLINVAR_FTP, output_path_gz, desc="Downloading ClinVar")

    if not success:
        return False

    # Decompress
    print("📦 Decompressing ClinVar data...")
    try:
        with gzip.open(output_path_gz, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"✅ Decompressed: {output_path}")

        # Remove gz file to save space
        output_path_gz.unlink()

        # Quick stats
        import pandas as pd

        df = pd.read_csv(output_path, sep="\t", low_memory=False)
        print(f"   Total variants: {len(df):,}")

        # Filter for BRCA1
        brca1_df = df[df["GeneSymbol"] == TARGET_GENE]
        print(f"   BRCA1 variants: {len(brca1_df):,}")

        # Save filtered version
        filtered_path = DATA_DIR / "clinvar_brca1.txt"
        brca1_df.to_csv(filtered_path, sep="\t", index=False)
        print(f"✅ Saved BRCA1-only dataset: {filtered_path}")

        return True
    except Exception as e:
        print(f"❌ Error decompressing: {e}")
        return False


def download_reference_sequence():
    """
    Download BRCA1 reference sequence from Ensembl
    This is needed for generating genomic context windows
    """
    print("\n📥 Downloading BRCA1 reference sequence...")

    # BRCA1 is on chromosome 17: 43,044,295-43,170,245 (GRCh38)
    # Using Ensembl REST API
    ensembl_url = "https://rest.ensembl.org/sequence/id/ENSG00000012048"
    params = {"content-type": "application/json", "type": "genomic"}

    try:
        response = requests.get(ensembl_url, params=params)
        response.raise_for_status()

        seq_data = response.json()
        sequence = seq_data["seq"]

        output_path = DATA_DIR / "brca1_reference_sequence.fasta"
        with open(output_path, "w") as f:
            f.write(f">ENSG00000012048 BRCA1 GRCh38\n")
            # Write in 80 character lines (FASTA format)
            for i in range(0, len(sequence), 80):
                f.write(sequence[i : i + 80] + "\n")

        print(f"✅ Downloaded BRCA1 reference sequence ({len(sequence):,} bp)")
        print(f"   Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading reference sequence: {e}")
        print("   This is optional - we can use variant sequences directly")
        return False


def main():
    """Main download function"""
    print("=" * 60)
    print("EvoMed Lightweight Model - Data Download")
    print("=" * 60)

    # Create data directory
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    print(f"📁 Data directory: {DATA_DIR}")

    # Download datasets
    results = {
        "BRCA Exchange": download_brca_exchange(),
        "ClinVar": download_clinvar(),
        "Reference Sequence": download_reference_sequence(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary:")
    print("=" * 60)
    for dataset, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{dataset:.<40} {status}")

    all_success = all(results.values())
    if all_success:
        print("\n🎉 All datasets downloaded successfully!")
        print("\n📋 Next steps:")
        print("   1. Set your HuggingFace token: export HF_TOKEN='your_token'")
        print("   2. Run data preparation: python scripts/prepare_training_data.py")
    else:
        print("\n⚠️  Some downloads failed. Please check errors above.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
