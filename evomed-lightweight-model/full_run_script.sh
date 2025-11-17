#!/bin/bash
# Master script to run everything tonight before training
# This prepares everything for overnight training

set -e  # Exit on error

echo "================================================================"
echo "🧬 EvoMed Lightweight Model - Tonight's Preparation"
echo "================================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📋 This script will:"
echo "   1. Verify your setup"
echo "   2. Install dependencies"
echo "   3. Setup Modal secrets"
echo "   4. Download datasets"
echo "   5. Prepare training data"
echo "   6. Upload to Modal"
echo "   7. Launch overnight training"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Step 1: Verify setup
echo ""
echo "================================================"
echo "Step 1/7: Verifying Setup"
echo "================================================"
python scripts/verify_setup.py

# Step 2: Install dependencies
echo ""
echo "================================================"
echo "Step 2/7: Installing Dependencies"
echo "================================================"
pip install -r requirements.txt

# Step 3: Setup Modal secrets
echo ""
echo "================================================"
echo "Step 3/7: Setting up Modal Secrets"
echo "================================================"
./scripts/setup_modal_secrets.sh

# Step 4: Download datasets
echo ""
echo "================================================"
echo "Step 4/7: Downloading Datasets (~30 mins)"
echo "================================================"
python scripts/download_data.py

if [ $? -ne 0 ]; then
    echo "❌ Data download failed. Please check errors above."
    exit 1
fi

# Step 5: Prepare training data
echo ""
echo "================================================"
echo "Step 5/7: Preparing Training Data (~1-2 hours)"
echo "================================================"
python scripts/prepare_training_data.py

if [ $? -ne 0 ]; then
    echo "❌ Data preparation failed. Please check errors above."
    exit 1
fi

# Step 6: Upload to Modal
echo ""
echo "================================================"
echo "Step 6/7: Uploading Data to Modal (~10 mins)"
echo "================================================"
modal run scripts/upload_to_modal.py

if [ $? -ne 0 ]; then
    echo "❌ Upload to Modal failed. Please check errors above."
    exit 1
fi

# Step 7: Launch training
echo ""
echo "================================================"
echo "Step 7/7: Launching Overnight Training"
echo "================================================"
echo "⚠️  IMPORTANT: Training will take 6-8 hours"
echo "   This will run overnight on Modal's H100 GPU"
echo ""
read -p "Ready to launch training? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo ""
    echo "🚀 Launching training on Modal..."
    modal run training/train_modal.py

    echo ""
    echo "================================================================"
    echo "✅ Training Launched!"
    echo "================================================================"
    echo ""
    echo "📊 Monitor progress:"
    echo "   modal app logs evomed-lightweight-training"
    echo ""
    echo "⏰ Check back in ~8 hours!"
    echo ""
    echo "😴 Go to sleep - training will complete overnight"
    echo ""
    echo "🌅 Tomorrow morning:"
    echo "   1. Check training results: cat /models/training_results.json"
    echo "   2. Test inference: modal run inference/serve_model.py"
    echo "   3. Deploy endpoint: modal deploy inference/serve_model.py"
    echo ""
    echo "🎓 You're on track to graduate!"
    echo "================================================================"
else
    echo ""
    echo "⏸️  Training not launched. To launch later, run:"
    echo "   modal run training/train_modal.py"
fi

echo ""
echo "✅ All setup complete!"
