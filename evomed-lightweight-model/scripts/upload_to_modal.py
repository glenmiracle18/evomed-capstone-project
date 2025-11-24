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
    """Upload processed data to Modal volume"""
    import shutil
    from pathlib import Path

    print("📤 Uploading data to Modal volume...")

    # Local data directory
    local_data_dir = Path("/tmp/evomed-data/processed")

    if not local_data_dir.exists():
        print(f"❌ Data directory not found: {local_data_dir}")
        print("   Make sure to run prepare_training_data.py first!")
        return {"error": "Data not found"}

    # Upload to Modal volume
    remote_data_dir = Path("/data/processed")
    remote_data_dir.mkdir(parents=True, exist_ok=True)

    files_uploaded = []

    for file_path in local_data_dir.glob("*"):
        if file_path.is_file():
            dest_path = remote_data_dir / file_path.name
            shutil.copy(file_path, dest_path)
            files_uploaded.append(file_path.name)
            print(f"    Uploaded: {file_path.name}")

    # Commit the volume
    data_volume.commit()

    print(f"\n Uploaded {len(files_uploaded)} files to Modal volume")

    return {
        "files_uploaded": files_uploaded,
        "count": len(files_uploaded),
    }


@app.local_entrypoint()
def main():
    """Local entrypoint to upload data"""
    import shutil
    from pathlib import Path

    print("=" * 60)
    print("Uploading Training Data to Modal")
    print("=" * 60)

    # Copy local data to /tmp for Modal access
    local_processed = DATA_DIR / "processed"
    temp_dir = Path("/tmp/evomed-data/processed")

    if not local_processed.exists():
        print(f"\n❌ Processed data not found: {local_processed}")
        print("   Please run: python scripts/prepare_training_data.py")
        return 1

    print(f"\n📁 Copying data to temp directory...")
    temp_dir.mkdir(parents=True, exist_ok=True)

    for file_path in local_processed.glob("*"):
        if file_path.is_file():
            shutil.copy(file_path, temp_dir / file_path.name)
            print(f"   Copied: {file_path.name}")

    # Upload to Modal
    print(f"\n🚀 Uploading to Modal volume...")
    result = upload_data.remote()

    if "error" in result:
        print(f"\n❌ Upload failed: {result['error']}")
        return 1

    print(f"\n Upload complete! {result['count']} files uploaded.")
    print("\n Next step:")
    print("   modal run training/train_modal.py")

    return 0


if __name__ == "__main__":
    exit(main())
