"""
Upload training data to Modal volume
"""

from pathlib import Path

import modal

app = modal.App("upload-training-data")

# Create volume
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)


@app.function(volumes={"/data": data_volume})
def upload_data():
    """Upload processed training data to Modal volume"""
    import shutil
    from pathlib import Path

    print("📤 Uploading training data to Modal volume...")

    # Local paths
    local_data_dir = Path(__file__).parent.parent / "data" / "processed"

    # Remote paths in Modal volume
    remote_data_dir = Path("/data/processed")
    remote_data_dir.mkdir(parents=True, exist_ok=True)

    # Upload files
    files_to_upload = ["train.csv", "val.csv", "test.csv", "metadata.json"]

    for filename in files_to_upload:
        local_path = local_data_dir / filename
        remote_path = remote_data_dir / filename

        if local_path.exists():
            shutil.copy(local_path, remote_path)
            print(f"   ✅ Uploaded {filename}")
        else:
            print(f"   ❌ File not found: {filename}")

    # Commit changes to volume
    data_volume.commit()
    print("\n✅ Training data uploaded successfully!")
    print("   Volume: evomed-training-data")
    print("   Path: /data/processed/")

    return "Upload complete"


@app.local_entrypoint()
def main():
    """Upload training data"""
    print("=" * 60)
    print("Uploading Training Data to Modal")
    print("=" * 60)

    result = upload_data.remote()
    print(f"\n{result}")

    print("\n📋 Next step:")
    print("   Run training: modal run training/train_modal.py")


if __name__ == "__main__":
    main()
