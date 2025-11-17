# DNABERT-2 Training Guide

## ✅ Current Status
- **Data Prepared**: 3,893 BRCA1 variants (Train: 3,114 | Val: 389 | Test: 390)
- **Model**: DNABERT-2-117M with LoRA fine-tuning
- **Platform**: Modal with GPU support

## 🚀 Next Steps to Train the Model

### Step 1: Set Up HuggingFace Token (If Not Already Done)

1. Get your HuggingFace token from: https://huggingface.co/settings/tokens
2. Create a Modal secret:

```bash
cd evomed-lightweight-model
source venv/bin/activate
modal secret create huggingface-secret HF_TOKEN=your_token_here
```

### Step 2: Upload Training Data to Modal

```bash
modal run scripts/upload_training_data.py
```

This uploads your 3,893 prepared variants to Modal's persistent volume.

### Step 3: Start Training

```bash
modal run training/train_modal.py
```

This will:
- Load DNABERT-2-117M model
- Apply LoRA for efficient fine-tuning
- Train on H100 GPU for ~30-60 minutes
- Save the trained model to Modal volume

**Training Configuration:**
- GPU: H100 (powerful!)
- Batch Size: 16
- Learning Rate: 2e-5
- Epochs: 3
- LoRA: r=8, alpha=16

### Step 4: Test Inference

After training completes, test the model:

```bash
modal run inference/serve_model.py::test_inference
```

---

## 📊 Expected Results

Based on the Findlay dataset:
- **Accuracy**: ~85-90% expected
- **Pathogenic Detection**: 21.1% of variants
- **Benign Detection**: 78.9% of variants

## 🔧 Troubleshooting

### "HuggingFace token not found"
Run: `modal secret create huggingface-secret HF_TOKEN=your_token`

### "Training data not found"
Run: `modal run scripts/upload_training_data.py`

### "Out of memory"
Reduce batch size in `configs/config.py`: `BATCH_SIZE = 8`

---

## 📝 What's Happening

1. **DNABERT-2** is a DNA foundation model pre-trained on genomic sequences
2. **LoRA** allows efficient fine-tuning with minimal GPU memory
3. **Findlay Dataset** provides high-quality functional scores for BRCA1 variants
4. **Modal** provides cloud GPU infrastructure for training

The model learns to classify BRCA1 variants as:
- **Pathogenic (LOF)**: Loss of function variants
- **Benign (FUNC)**: Functional variants

## 🎯 After Training

Once trained, you can:
1. Deploy as a web API endpoint
2. Make predictions on new variants
3. Apply African population adjustments
4. Integrate with BRCA Exchange API for live data

---

**Ready to train?** Run the commands above in order! 🚀
