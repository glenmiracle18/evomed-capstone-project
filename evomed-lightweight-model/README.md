# EvoMed Lightweight Variant Classifier

Fast, African population-aware BRCA1 variant pathogenicity classifier using DNABERT-2

## Quick Start

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Set HuggingFace Token
```bash
export HF_TOKEN="your_hf_token_here"
```

### 3. Download & Prepare Data
```bash
python scripts/download_data.py
python scripts/prepare_training_data.py
```

### 4. Train Model (Overnight)
```bash
modal run training/train_modal.py
```

### 5. Deploy Model
```bash
modal deploy inference/serve_model.py
```

## Timeline
- **Tonight:** Data preparation (3-4 hours)
- **Overnight:** Training (6-8 hours automated)
- **Tomorrow:** Integration & testing (4-5 hours)

## Model Details
- **Base Model:** DNABERT-2 (117M parameters)
- **Task:** BRCA1 variant pathogenicity classification
- **Training Data:** BRCA Exchange + ClinVar (~10K variants)
- **African Population Focus:** gnomAD AFR subset
- **Expected Performance:** 82-88% accuracy, ~100ms inference

## Directory Structure
```
evomed-lightweight-model/
├── data/              # Downloaded datasets
├── scripts/           # Data download & preprocessing
├── training/          # Model training code
├── inference/         # Deployment & serving
├── tests/             # Testing scripts
└── configs/           # Configuration files
```
