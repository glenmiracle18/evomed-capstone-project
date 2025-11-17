#!/bin/bash
# Setup Modal secrets for HuggingFace authentication

echo "============================================================"
echo "Setting up Modal Secrets for DNABERT-2 Training"
echo "============================================================"

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null; then
    echo "❌ Modal CLI not found. Installing..."
    pip install modal
fi

# Check if user is logged in to Modal
echo ""
echo "📋 Checking Modal authentication..."
if ! modal token set --help &> /dev/null; then
    echo "⚠️  Please authenticate with Modal first:"
    echo "   modal token set"
    exit 1
fi

# Prompt for HuggingFace token
echo ""
echo "🔑 Please enter your HuggingFace token:"
echo "   (Get it from: https://huggingface.co/settings/tokens)"
read -sp "HF_TOKEN: " HF_TOKEN
echo ""

if [ -z "$HF_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Create Modal secret
echo ""
echo "📤 Creating Modal secret 'huggingface-secret'..."
modal secret create huggingface-secret HF_TOKEN="$HF_TOKEN"

if [ $? -eq 0 ]; then
    echo "✅ Secret created successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Download data: python scripts/download_data.py"
    echo "   2. Prepare data: python scripts/prepare_training_data.py"
    echo "   3. Upload to Modal: modal run scripts/upload_to_modal.py"
    echo "   4. Start training: modal run training/train_modal.py"
else
    echo "❌ Failed to create secret. Please try manually:"
    echo "   modal secret create huggingface-secret HF_TOKEN='your_token'"
    exit 1
fi
