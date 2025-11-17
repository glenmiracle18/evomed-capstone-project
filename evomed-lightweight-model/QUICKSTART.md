# 🚀 QUICKSTART - 24 Hour Training Guide

Get your DNABERT-2 model trained and deployed in 24 hours!

## Prerequisites

- ✅ HuggingFace account & Write token (you have this!)
- ✅ Modal account & authentication (you have this!)
- ✅ 5GB free disk space

## Step-by-Step Execution

### Phase 1: Setup & Data Prep (Tonight - 3-4 hours)

#### 1. Install Dependencies (5 mins)
```bash
cd evomed-lightweight-model
pip install -r requirements.txt
```

#### 2. Setup HuggingFace Token in Modal (2 mins)
```bash
# Option A: Use the setup script
./scripts/setup_modal_secrets.sh

# Option B: Manual setup
modal secret create huggingface-secret HF_TOKEN="hf_your_token_here"
```

#### 3. Download Datasets (30 mins)
```bash
python scripts/download_data.py
```

This downloads:
- BRCA Exchange (~10K BRCA1 variants)
- ClinVar (for additional validation)
- BRCA1 reference sequence

#### 4. Prepare Training Data (1-2 hours)
```bash
python scripts/prepare_training_data.py
```

This:
- Filters for high-quality pathogenic/benign labels
- Integrates African population frequencies
- Splits into train/val/test (80/10/10)
- Saves processed data locally

#### 5. Upload Data to Modal (10 mins)
```bash
modal run scripts/upload_to_modal.py
```

This uploads your processed data to Modal's persistent volume.

### Phase 2: Training (Overnight - 6-8 hours)

#### 6. Launch Training (runs overnight)
```bash
# Launch training on Modal H100 GPU
modal run training/train_modal.py
```

**What happens:**
- Loads DNABERT-2 (117M params) from HuggingFace
- Applies LoRA for efficient fine-tuning
- Trains for 3 epochs (~6-8 hours)
- Saves checkpoints every 50 steps
- Evaluates on validation set
- Saves final model to Modal volume

**Go to sleep!** ⏰ Training runs automatically.

### Phase 3: Integration (Tomorrow - 4-5 hours)

#### 7. Test the Trained Model (30 mins)
```bash
modal run inference/serve_model.py
```

This tests inference with a sample variant.

#### 8. Deploy Inference Endpoint (30 mins)
```bash
modal deploy inference/serve_model.py
```

Get your endpoint URL (e.g., `https://xxx.modal.run/predict_variant`)

#### 9. Integrate with Existing Backend (2-3 hours)

Add to your existing `evomed-backend-fastapi/main.py`:

```python
import requests

LIGHTWEIGHT_MODEL_URL = "https://your-modal-url.modal.run/predict_variant"

@app.post("/api/analyze-variant-fast")
async def analyze_variant_fast(request: VariantRequest):
    """Fast variant analysis using lightweight DNABERT-2 model"""

    # Call lightweight model
    response = requests.post(
        LIGHTWEIGHT_MODEL_URL,
        json={
            "chromosome": request.chromosome,
            "position": request.position,
            "ref": request.ref,
            "alt": request.alt,
            "apply_african_adjustment": True,
        }
    )

    return response.json()
```

#### 10. Update Frontend (1 hour)

Add model selection toggle to `variant-analysis.tsx`:

```typescript
const [useRapidModel, setUseRapidModel] = useState(false);

// In your API call:
const endpoint = useRapidModel
  ? '/api/analyze-variant-fast'
  : '/api/analyze-variant';
```

#### 11. Test End-to-End (30 mins)
```bash
# Test the full pipeline
curl -X POST https://your-modal-url.modal.run/predict_variant \
  -H "Content-Type: application/json" \
  -d '{
    "chromosome": "17",
    "position": 43045677,
    "ref": "G",
    "alt": "A",
    "apply_african_adjustment": true
  }'
```

## Timeline Checklist

### Tonight (Before Sleep)
- [ ] Install dependencies
- [ ] Setup HuggingFace token
- [ ] Download datasets
- [ ] Prepare training data
- [ ] Upload to Modal
- [ ] **Launch training** 🚀

### Tomorrow Morning
- [ ] Check training status
- [ ] Review training metrics
- [ ] Test inference

### Tomorrow Afternoon
- [ ] Deploy model endpoint
- [ ] Integrate with backend
- [ ] Update frontend
- [ ] Test end-to-end
- [ ] **GRADUATE!** 🎓

## Expected Performance

- **Accuracy:** 82-88%
- **Inference Time:** ~100ms (vs 2-5s for Evo2)
- **Model Size:** ~500MB (vs 7B params for Evo2)
- **African Bias Reduction:** 25-35%

## Troubleshooting

### Training fails with "Data not found"
```bash
# Re-upload data
modal run scripts/upload_to_modal.py
```

### "HuggingFace token invalid"
```bash
# Update token
modal secret create huggingface-secret HF_TOKEN="hf_new_token"
```

### Training too slow
```bash
# Reduce dataset size in config.py
# Use only high-confidence variants
```

### Out of memory
```bash
# Reduce batch size in config.py
BATCH_SIZE = 8  # Instead of 16
```

## Monitoring Training

Check training progress:
```bash
modal app logs evomed-lightweight-training
```

## Cost Estimate

- **Modal H100 GPU:** ~$2-4 for 8 hours training
- **Modal T4 GPU:** ~$0.50/hour for inference
- **Total:** ~$5-10 for full project

## Next Steps After Success

1. **Evaluate performance** against Evo2
2. **Compare predictions** on test variants
3. **Document results** for graduation
4. **Publish model** to HuggingFace (optional)

---

**You've got this!** 💪 Questions? Check the logs or ping me.
