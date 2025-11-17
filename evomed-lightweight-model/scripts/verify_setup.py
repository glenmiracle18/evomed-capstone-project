"""
Verify that everything is set up correctly before training
"""
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        'modal',
        'pandas',
        'numpy',
        'requests',
        'tqdm',
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False

    return True

def check_modal_auth():
    """Check if Modal is authenticated"""
    print("\n🔍 Checking Modal authentication...")

    try:
        import subprocess
        result = subprocess.run(
            ['modal', 'token', 'current'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("   ✅ Modal authenticated")
            return True
        else:
            print("   ❌ Not authenticated")
            print("   Run: modal token set")
            return False
    except FileNotFoundError:
        print("   ❌ Modal CLI not found")
        print("   Install with: pip install modal")
        return False
    except Exception as e:
        print(f"   ⚠️  Could not verify: {e}")
        return False

def check_hf_token():
    """Check if HuggingFace token is set"""
    print("\n🔍 Checking HuggingFace token...")

    import os
    token = os.getenv('HF_TOKEN')

    if token:
        print(f"   ✅ Token found (starts with: {token[:10]}...)")
        return True
    else:
        print("   ⚠️  HF_TOKEN environment variable not set")
        print("   You'll need to set this or create a Modal secret")
        print("   Run: ./scripts/setup_modal_secrets.sh")
        return True  # Not critical for local checks

def check_disk_space():
    """Check available disk space"""
    print("\n🔍 Checking disk space...")

    import shutil
    stats = shutil.disk_usage(".")

    free_gb = stats.free / (1024**3)
    print(f"   Free space: {free_gb:.1f} GB")

    if free_gb < 5:
        print("   ⚠️  Low disk space! Need at least 5GB")
        return False
    else:
        print("   ✅ Sufficient disk space")
        return True

def check_data_files():
    """Check if data files are ready"""
    print("\n🔍 Checking data files...")

    sys.path.append(str(Path(__file__).parent.parent))
    from configs.config import DATA_DIR

    # Check raw data
    raw_files = [
        DATA_DIR / "brca_exchange_brca1.tsv",
        DATA_DIR / "clinvar_brca1.txt",
    ]

    raw_ok = all(f.exists() for f in raw_files)
    if raw_ok:
        print("   ✅ Raw data downloaded")
    else:
        print("   ⚠️  Raw data not found")
        print("   Run: python scripts/download_data.py")

    # Check processed data
    processed_dir = DATA_DIR / "processed"
    processed_files = [
        processed_dir / "train.csv",
        processed_dir / "val.csv",
        processed_dir / "test.csv",
    ]

    processed_ok = all(f.exists() for f in processed_files)
    if processed_ok:
        print("   ✅ Processed data ready")

        # Show stats
        import pandas as pd
        train_df = pd.read_csv(processed_files[0])
        val_df = pd.read_csv(processed_files[1])
        test_df = pd.read_csv(processed_files[2])

        total = len(train_df) + len(val_df) + len(test_df)
        print(f"      Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,} | Total: {total:,}")
    else:
        print("   ⚠️  Processed data not found")
        print("   Run: python scripts/prepare_training_data.py")

    return raw_ok or processed_ok

def check_modal_volumes():
    """Check if Modal volumes are accessible"""
    print("\n🔍 Checking Modal volumes...")

    try:
        import subprocess
        result = subprocess.run(
            ['modal', 'volume', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Check for our specific volumes
            volumes = result.stdout

            has_data = 'evomed-training-data' in volumes
            has_model = 'evomed-trained-models' in volumes

            if has_data:
                print("   ✅ evomed-training-data volume exists")
            else:
                print("   ⚠️  evomed-training-data volume will be created on first run")

            if has_model:
                print("   ✅ evomed-trained-models volume exists")
            else:
                print("   ⚠️  evomed-trained-models volume will be created on first run")

            return True
        else:
            print("   ⚠️  Could not list volumes")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not check volumes: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("EvoMed Lightweight Model - Setup Verification")
    print("=" * 60)

    checks = {
        "Dependencies": check_dependencies(),
        "Modal Auth": check_modal_auth(),
        "HuggingFace Token": check_hf_token(),
        "Disk Space": check_disk_space(),
        "Data Files": check_data_files(),
        "Modal Volumes": check_modal_volumes(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{name:.<40} {status}")

    critical_checks = ["Dependencies", "Modal Auth", "Disk Space"]
    critical_passed = all(checks[name] for name in critical_checks)

    print("\n" + "=" * 60)
    if critical_passed:
        print("✅ Critical checks passed! You're ready to proceed.")

        # Next steps
        print("\n📋 Next steps:")

        if not checks["Data Files"]:
            print("   1. Download data: python scripts/download_data.py")
            print("   2. Prepare data: python scripts/prepare_training_data.py")
            print("   3. Upload to Modal: modal run scripts/upload_to_modal.py")
        else:
            print("   1. Upload to Modal: modal run scripts/upload_to_modal.py")

        print("   2. Start training: modal run training/train_modal.py")
    else:
        print("❌ Some critical checks failed. Please fix the issues above.")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
