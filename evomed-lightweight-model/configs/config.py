"""
Configuration file for lightweight BRCA1 variant classifier
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# Data sources
BRCA_EXCHANGE_URL = "https://brcaexchange.org/backend/downloads/releases/release-12-06-23/built_with_change_types.tsv"
CLINVAR_FTP = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"

# Target gene
TARGET_GENE = "BRCA1"
GENE_CHROMOSOME = "17"

# gnomAD populations of interest
AFRICAN_POPULATIONS = [
    "afr",  # African/African American
    "asj",  # Ashkenazi Jewish (for comparison)
]

# Model configuration
MODEL_NAME = "zhihan1996/DNABERT-2-117M"
MAX_SEQUENCE_LENGTH = 512  # DNABERT-2 can handle longer, but 512 is fast
GENOMIC_CONTEXT_WINDOW = 256  # bp on each side of variant

# Training configuration
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
NUM_EPOCHS = 3
WARMUP_STEPS = 100
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 1.0

# LoRA configuration (for efficient fine-tuning)
USE_LORA = True
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.1
LORA_TARGET_MODULES = ["query", "value"]

# Data split
TRAIN_SPLIT = 0.8
VAL_SPLIT = 0.1
TEST_SPLIT = 0.1

# Classification thresholds
PATHOGENIC_THRESHOLD = 0.5
HIGH_CONFIDENCE_THRESHOLD = 0.7

# African population adjustment (similar to your existing approach)
AFRICAN_ADJUSTMENT_THRESHOLDS = {
    "high": 0.05,      # AF > 5%: strong benign evidence
    "medium": 0.01,    # AF > 1%: moderate evidence
    "low": 0.005,      # AF > 0.5%: mild evidence
}

AFRICAN_ADJUSTMENT_SCORES = {
    "high": 0.15,      # Larger adjustment for training
    "medium": 0.10,
    "low": 0.05,
}

# Modal configuration
MODAL_GPU = "H100"
MODAL_TIMEOUT = 3600  # 1 hour for training
MODAL_CPU = 4
MODAL_MEMORY = 16384  # 16GB

# Logging
LOG_LEVEL = "INFO"
WANDB_PROJECT = "evomed-lightweight-brca1"  # Optional: Weights & Biases tracking

# HuggingFace
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Random seed for reproducibility
RANDOM_SEED = 42
