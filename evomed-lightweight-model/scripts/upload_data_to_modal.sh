#!/bin/bash

# Upload preprocessed data to Modal volume
# Run this once before training

echo "Uploading preprocessed data to Modal volume..."

modal volume put evomed-training-data data/processed/train.csv /data/train.csv
modal volume put evomed-training-data data/processed/val.csv /data/val.csv
modal volume put evomed-training-data data/processed/test.csv /data/test.csv

echo "✅ Data upload complete!"
echo ""
echo "Now you can run: modal run training/train_random_forest_modal.py"
