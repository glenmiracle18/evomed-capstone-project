"""
Upload processed training data to Modal volume
"""

import sys
from pathlib import Path

import modal

sys.path.append(str(Path(__file__).parent.parent))
from configs.config import DATA_DIR

app = modal.App("evomed-data-upload")

# Reference the same volume used in training
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)


@app.function(volumes={"/data": data_volume}, timeout=600)
def upload_data():
    """Upload variants dataset to Modal volume"""
    import shutil
    from pathlib import Path

    print("Uploading data to Modal volume...")

    # Upload the variants dataset directly
    local_variants_file = Path("/tmp/evomed-data/variants(1).tsv")
    
    if not local_variants_file.exists():
        print(f"Data file not found: {local_variants_file}")
        print("   Make sure variants(1).tsv is available!")
        return {"error": "Data not found"}

    # Copy variants file to Modal volume
    remote_variants_file = Path("/data/variants(1).tsv")
    shutil.copy(local_variants_file, remote_variants_file)
    print(f"   Uploaded: variants(1).tsv")

    # Commit the volume
    data_volume.commit()

    print(f" Data uploaded successfully to Modal volume")

    return {
        "files_uploaded": ["variants(1).tsv"],
        "count": 1,
    }


def main():
    """Local function to upload data"""
    import shutil
    from pathlib import Path

    print("=" * 60)
    print("Uploading Training Data to Modal")
    print("=" * 60)

    # Copy variants dataset to /tmp for Modal access
    local_variants = DATA_DIR / "variants(1).tsv"
    temp_dir = Path("/tmp/evomed-data")

    if not local_variants.exists():
        print(f"\nVariants file not found: {local_variants}")
        print("   Please ensure variants(1).tsv is in the data directory")
        return 1

    print(f"\nCopying data to temp directory...")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_variants = temp_dir / "variants(1).tsv"
    shutil.copy(local_variants, temp_variants)
    print(f"   Copied: variants(1).tsv")

    print(f"\nNext step:")
    print("   Run: modal run scripts/upload_to_modal.py::upload_data")
    print("   Then: modal run training/train_modal.py")

    return 0


if __name__ == "__main__":
    exit(main())
