"""
Modal training script for DNABERT-2 fine-tuning on BRCA1 variant pathogenicity
"""

import sys
from pathlib import Path

import modal

# Modal app definition
app = modal.App("evomed-lightweight-training")

# Create Modal image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch>=2.0.0",
    "transformers>=4.35.0",
    "datasets>=2.14.0",
    "accelerate>=0.24.0",
    "peft>=0.6.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "biopython>=1.81",
    "scikit-learn>=1.3.0",
    "tqdm>=4.66.0",
    "requests>=2.31.0",
)

# Create Modal volumes for data persistence
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)
model_volume = modal.Volume.from_name("evomed-trained-models", create_if_missing=True)


@app.function(
    image=image,
    gpu="H100",
    timeout=7200,  # 2 hours
    volumes={
        "/data": data_volume,
        "/models": model_volume,
    },
    secrets=[modal.Secret.from_name("huggingface-secret")],  # You'll create this
)
def train_dnabert2():
    """
    Fine-tune DNABERT-2 on BRCA1 variant pathogenicity classification
    """
    import json
    import os
    from datetime import datetime

    import numpy as np
    import pandas as pd
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from sklearn.metrics import (
        accuracy_score,
        precision_recall_fscore_support,
        roc_auc_score,
    )
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
    )

    print("=" * 70)
    print("🧬 EvoMed Lightweight Model - DNABERT-2 Training")
    print("=" * 70)

    # Configuration
    MODEL_NAME = "zhihan1996/DNABERT-2-117M"
    MAX_LENGTH = 512
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 3
    WARMUP_STEPS = 100

    # LoRA config
    LORA_R = 8
    LORA_ALPHA = 16
    LORA_DROPOUT = 0.1

    # Set random seed
    SEED = 42
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    # Check GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️  Device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(
            f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
        )

    # Load datasets
    print("\n📂 Loading datasets...")
    try:
        train_df = pd.read_csv("/data/processed/train.csv")
        val_df = pd.read_csv("/data/processed/val.csv")
        test_df = pd.read_csv("/data/processed/test.csv")

        print(f"   Train: {len(train_df):,} variants")
        print(f"   Val: {len(val_df):,} variants")
        print(f"   Test: {len(test_df):,} variants")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("   Make sure to upload processed data to Modal volume first!")
        return {"error": str(e)}

    # Load tokenizer and model
    print(f"\n🤖 Loading DNABERT-2 model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    # For now, we'll use a simple approach with sequence representation
    # In production, you'd fetch actual genomic sequences
    def prepare_sequence(row):
        """
        Prepare DNA sequence for the model
        """
        ref = str(row["ref"])[: MAX_LENGTH // 2]
        alt = str(row["alt"])[: MAX_LENGTH // 2]

        # Pad with N's to create context
        context_size = MAX_LENGTH // 4
        padding = "N" * context_size

        # Alternate sequence: padding + variant + padding
        sequence = padding + alt + padding

        return sequence

    # Prepare datasets
    print("\n🔄 Preparing sequences...")

    def df_to_dataset(df):
        """Convert DataFrame to HuggingFace Dataset"""
        sequences = []
        labels = []

        for _, row in df.iterrows():
            try:
                seq = prepare_sequence(row)
                sequences.append(seq)
                labels.append(int(row["label"]))
            except Exception as e:
                print(f"   Warning: Skipping row due to error: {e}")
                continue

        return Dataset.from_dict(
            {
                "sequence": sequences,
                "label": labels,
            }
        )

    train_dataset = df_to_dataset(train_df)
    val_dataset = df_to_dataset(val_df)
    test_dataset = df_to_dataset(test_df)

    print(f"   ✅ Train dataset: {len(train_dataset)} samples")
    print(f"   ✅ Val dataset: {len(val_dataset)} samples")
    print(f"   ✅ Test dataset: {len(test_dataset)} samples")

    # Tokenize datasets
    print("\n🔤 Tokenizing sequences...")

    def tokenize_function(examples):
        return tokenizer(
            examples["sequence"],
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
        )

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)

    # Load model
    print(f"\n🚀 Loading model for sequence classification...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        trust_remote_code=True,
    )

    # Apply LoRA
    print("\n⚡ Applying LoRA for efficient fine-tuning...")
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["query", "value"],
        inference_mode=False,
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Training arguments
    output_dir = "/models/dnabert2-brca1-checkpoints"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=WARMUP_STEPS,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        logging_dir="/models/logs",
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,  # Mixed precision training
        dataloader_num_workers=4,
        report_to="none",  # Disable wandb for now
    )

    # Metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)

        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="binary"
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    # Trainer
    print("\n🏋️  Initializing Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    # Train!
    print("\n" + "=" * 70)
    print("🚀 Starting Training...")
    print("=" * 70)
    train_result = trainer.train()

    # Save final model
    print("\n💾 Saving final model...")
    final_model_path = "/models/dnabert2-brca1-final"
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)

    # Evaluate on test set
    print("\n📊 Evaluating on test set...")
    test_results = trainer.evaluate(test_dataset)

    # Get predictions for more detailed metrics
    predictions = trainer.predict(test_dataset)
    pred_probs = torch.softmax(torch.tensor(predictions.predictions), dim=1)[
        :, 1
    ].numpy()
    pred_labels = np.argmax(predictions.predictions, axis=1)
    true_labels = predictions.label_ids

    # Calculate additional metrics
    try:
        auc = roc_auc_score(true_labels, pred_probs)
        test_results["auc"] = auc
    except Exception as e:
        print(f"   Warning: Could not calculate AUC: {e}")

    # Calculate metrics by class
    pathogenic_mask = true_labels == 1
    benign_mask = true_labels == 0

    pathogenic_acc = accuracy_score(
        true_labels[pathogenic_mask], pred_labels[pathogenic_mask]
    )
    benign_acc = accuracy_score(true_labels[benign_mask], pred_labels[benign_mask])

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "model_name": MODEL_NAME,
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset),
        "test_samples": len(test_dataset),
        "num_epochs": NUM_EPOCHS,
        "learning_rate": LEARNING_RATE,
        "batch_size": BATCH_SIZE,
        "test_results": {k: float(v) for k, v in test_results.items()},
        "pathogenic_accuracy": float(pathogenic_acc),
        "benign_accuracy": float(benign_acc),
    }

    results_path = "/models/training_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("✅ Training Complete!")
    print("=" * 70)
    print(f"\n📊 Test Results:")
    print(f"   Accuracy: {test_results.get('eval_accuracy', 0):.4f}")
    print(f"   Precision: {test_results.get('eval_precision', 0):.4f}")
    print(f"   Recall: {test_results.get('eval_recall', 0):.4f}")
    print(f"   F1 Score: {test_results.get('eval_f1', 0):.4f}")
    if "auc" in test_results:
        print(f"   AUC: {test_results['auc']:.4f}")
    print(f"\n   Pathogenic Accuracy: {pathogenic_acc:.4f}")
    print(f"   Benign Accuracy: {benign_acc:.4f}")

    print(f"\n💾 Model saved to: {final_model_path}")
    print(f"📊 Results saved to: {results_path}")

    return results


@app.local_entrypoint()
def main():
    """Local entrypoint to trigger training"""
    print("🚀 Launching DNABERT-2 training on Modal...")
    result = train_dnabert2.remote()

    print("\n" + "=" * 70)
    if "error" in result:
        print(f"❌ Training failed: {result['error']}")
    else:
        print("✅ Training completed successfully!")
        print("\n📊 Results:")
        import json

        print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    main()
