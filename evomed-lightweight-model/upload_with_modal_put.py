#!/usr/bin/env python3
"""
Upload variants dataset to Modal volume using modal volume put
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("Uploading variants dataset to Modal")
    print("=" * 60)
    
    # Check if variants file exists
    variants_file = Path("data/variants(1).tsv")
    if not variants_file.exists():
        print(f"Error: Variants file not found at {variants_file}")
        return 1
    
    file_size = variants_file.stat().st_size / 1024 / 1024
    print(f"File size: {file_size:.1f} MB")
    
    volume_name = "evomed-training-data"
    
    # Check if volume exists, create if not
    print(f"\nChecking if volume '{volume_name}' exists...")
    
    list_cmd = ["modal", "volume", "list"]
    list_result = subprocess.run(list_cmd, capture_output=True, text=True)
    
    if volume_name not in list_result.stdout:
        print(f"Volume '{volume_name}' not found. Creating it...")
        create_cmd = ["modal", "volume", "create", volume_name]
        create_result = subprocess.run(create_cmd, capture_output=True, text=True)
        
        if create_result.returncode == 0:
            print(f"✅ Volume '{volume_name}' created successfully")
        else:
            print(f"❌ Failed to create volume: {create_result.stderr}")
            return 1
    else:
        print(f"✅ Volume '{volume_name}' exists")
        
        # Check if file already exists in volume
        print("Checking if variants file already exists in volume...")
        ls_cmd = ["modal", "volume", "ls", volume_name]
        ls_result = subprocess.run(ls_cmd, capture_output=True, text=True)
        
        if "variants(1).tsv" in ls_result.stdout:
            print("⚠️  File 'variants(1).tsv' already exists in volume")
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Upload cancelled")
                return 0
    
    # Upload using modal volume put
    print(f"\nUploading to Modal volume '{volume_name}'...")
    
    try:
        cmd = [
            "modal", "volume", "put", 
            volume_name,
            str(variants_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Upload successful!")
            if result.stdout.strip():
                print("Output:", result.stdout)
        else:
            print("❌ Upload failed!")
            print("Error:", result.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return 1
    
    print("\n🎉 Ready to train!")
    print("Next step: modal run training/train_modal.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())