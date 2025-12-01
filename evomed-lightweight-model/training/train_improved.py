"""
Improved Modal training script with comprehensive evaluation metrics and class weighting
Addresses all defense feedback about model performance and evaluation
"""

import sys
from pathlib import Path

import modal

# Modal app definition
app = modal.App("evomed-training-improved")

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
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "plotly>=5.17.0",
    "imbalanced-learn>=0.11.0",  # For SMOTE and class weighting utilities
)

# Create Modal volumes for data persistence
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)
model_volume = modal.Volume.from_name("evomed-trained-models", create_if_missing=True)


@app.function(
    image=image,
    gpu="A100",
    timeout=7200,  # 2 hours
    volumes={
        "/data": data_volume,
        "/models": model_volume,
    },
)
def train_with_comprehensive_metrics():
    """
    Fine-tune model with comprehensive evaluation metrics and class weighting
    Addresses defense feedback:
    1. Proper metrics for imbalanced data (F1, MCC, AUC-PR, Balanced Accuracy)
    2. Class weighting in loss function
    3. Overfitting/underfitting detection
    4. Per-class performance reporting
    """
    import json
    import os
    from datetime import datetime

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import torch
    import torch.nn as nn
    from datasets import Dataset
    from sklearn.metrics import (
        accuracy_score,
        auc,
        balanced_accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        matthews_corrcoef,
        precision_recall_curve,
        precision_recall_fscore_support,
        roc_auc_score,
        roc_curve,
    )
    from sklearn.model_selection import StratifiedKFold, train_test_split
    from transformers import (
        BertConfig,
        BertModel,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
    )

    print("=" * 80)
    print("EvoMed - Improved Training with Comprehensive Metrics")
    print("=" * 80)

    # Configuration
    MAX_LENGTH = 512
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 10  # Increased for better training
    WARMUP_STEPS = 100
    WEIGHT_DECAY = 0.01
    DROPOUT = 0.1
    GRADIENT_CLIP = 1.0

    SEED = 42
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    # Check GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️  Device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(
            f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
        )

    # ========================================================================
    # STEP 1: LOAD AND PREPARE DATA
    # ========================================================================
    print("\n📂 Loading dataset...")

    # Check if processed data exists
    if os.path.exists("/data/processed/train.csv"):
        print("   Using pre-processed data from data preparation script...")
        train_df = pd.read_csv("/data/processed/train.csv")
        val_df = pd.read_csv("/data/processed/val.csv")
        test_df = pd.read_csv("/data/processed/test.csv")

        print(f"   ✅ Train: {len(train_df):,} variants")
        print(f"   ✅ Val: {len(val_df):,} variants")
        print(f"   ✅ Test: {len(test_df):,} variants")
    else:
        print("   Processed data not found. Please run prepare_training_data.py first!")
        return {"error": "Processed data not found"}

    # Calculate class distribution and weights
    print("\n📊 Class Distribution Analysis...")

    pathogenic_train = (train_df["label"] == 1).sum()
    benign_train = (train_df["label"] == 0).sum()
    total_train = len(train_df)

    print(
        f"   Train - Pathogenic: {pathogenic_train:,} ({pathogenic_train / total_train * 100:.1f}%)"
    )
    print(
        f"   Train - Benign: {benign_train:,} ({benign_train / total_train * 100:.1f}%)"
    )
    print(
        f"   Imbalance Ratio: {max(pathogenic_train, benign_train) / min(pathogenic_train, benign_train):.2f}:1"
    )

    # Calculate class weights for loss function
    class_weights = torch.tensor(
        [
            total_train / (2 * benign_train),  # Weight for class 0 (Benign)
            total_train / (2 * pathogenic_train),  # Weight for class 1 (Pathogenic)
        ],
        dtype=torch.float32,
    )

    print(f"\n⚖️  Class Weights (for loss function):")
    print(f"   Benign (0): {class_weights[0]:.4f}")
    print(f"   Pathogenic (1): {class_weights[1]:.4f}")

    # ========================================================================
    # STEP 2: CREATE CUSTOM MODEL WITH WEIGHTED LOSS
    # ========================================================================
    print("\n🏗️  Building Custom Classification Model...")

    class DNASequenceClassifier(nn.Module):
        """
        Custom BERT-based classifier with weighted cross-entropy loss
        """

        def __init__(
            self, hidden_size=768, num_labels=2, dropout=0.1, class_weights=None
        ):
            super().__init__()

            # BERT backbone
            bert_config = BertConfig(
                vocab_size=1024,
                hidden_size=hidden_size,
                num_hidden_layers=6,
                num_attention_heads=12,
                intermediate_size=3072,
                max_position_embeddings=512,
                num_labels=num_labels,
                hidden_dropout_prob=dropout,
                attention_probs_dropout_prob=dropout,
            )

            self.bert = BertModel(bert_config)
            self.config = bert_config

            # Classification head
            self.dropout = nn.Dropout(dropout)
            self.classifier = nn.Linear(hidden_size, num_labels)
            self.num_labels = num_labels

            # Store class weights for weighted loss
            self.class_weights = class_weights

        def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
            # BERT forward pass
            outputs = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask,
                return_dict=True,
            )

            # Mean pooling of last hidden state
            pooled_output = outputs.last_hidden_state.mean(dim=1)
            pooled_output = self.dropout(pooled_output)
            logits = self.classifier(pooled_output)

            loss = None
            if labels is not None:
                # Use weighted cross-entropy loss
                if self.class_weights is not None:
                    loss_fct = nn.CrossEntropyLoss(
                        weight=self.class_weights.to(logits.device)
                    )
                else:
                    loss_fct = nn.CrossEntropyLoss()

                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))

            from transformers.modeling_outputs import SequenceClassifierOutput

            return SequenceClassifierOutput(
                loss=loss,
                logits=logits,
                hidden_states=outputs.hidden_states,
                attentions=outputs.attentions,
            )

    # Initialize model with class weights
    model = DNASequenceClassifier(
        hidden_size=768, num_labels=2, dropout=DROPOUT, class_weights=class_weights
    )

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   ✅ Model created")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")

    # ========================================================================
    # STEP 3: PREPARE DATASETS
    # ========================================================================
    print("\n🔤 Preparing sequences...")

    def prepare_sequence(row):
        """Create DNA sequence representation"""
        ref = str(row.get("ref", "N"))
        alt = str(row.get("alt", "N"))

        # Simple sequence representation (in production, fetch real genomic context)
        context_size = (MAX_LENGTH - len(alt)) // 2
        left_context = "N" * context_size
        right_context = "N" * (MAX_LENGTH - len(left_context) - len(alt))

        sequence = left_context + alt + right_context

        # Ensure exactly MAX_LENGTH
        if len(sequence) > MAX_LENGTH:
            sequence = sequence[:MAX_LENGTH]
        elif len(sequence) < MAX_LENGTH:
            sequence = sequence + "N" * (MAX_LENGTH - len(sequence))

        return sequence

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

    # Tokenize (simple character-level encoding for DNA)
    print("\n🔢 Tokenizing sequences...")

    # Create simple DNA vocabulary
    dna_vocab = {"N": 0, "A": 1, "C": 2, "G": 3, "T": 4, "<PAD>": 5}

    def tokenize_dna(sequence):
        """Convert DNA sequence to token IDs"""
        return [dna_vocab.get(base, 0) for base in sequence]

    def tokenize_function(examples):
        """Tokenize batch of sequences"""
        input_ids = [tokenize_dna(seq) for seq in examples["sequence"]]
        attention_mask = [[1] * len(ids) for ids in input_ids]

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)

    print("   ✅ Tokenization complete")

    # ========================================================================
    # STEP 4: COMPREHENSIVE METRICS COMPUTATION
    # ========================================================================

    def compute_comprehensive_metrics(eval_pred):
        """
        Compute comprehensive metrics suitable for imbalanced data
        Addresses defense feedback about using only accuracy
        """
        predictions, labels = eval_pred
        pred_probs = torch.softmax(torch.tensor(predictions), dim=1)[:, 1].numpy()
        pred_labels = np.argmax(predictions, axis=1)

        # Basic metrics
        accuracy = accuracy_score(labels, pred_labels)
        balanced_acc = balanced_accuracy_score(labels, pred_labels)

        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            labels, pred_labels, average=None, labels=[0, 1]
        )

        # Macro-averaged metrics (treats both classes equally)
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            labels, pred_labels, average="macro"
        )

        # Matthews Correlation Coefficient (best for imbalanced data)
        mcc = matthews_corrcoef(labels, pred_labels)

        # AUC metrics
        try:
            auc_roc = roc_auc_score(labels, pred_probs)

            # AUC-PR (better for imbalanced data)
            precision_curve, recall_curve, _ = precision_recall_curve(
                labels, pred_probs
            )
            auc_pr = auc(recall_curve, precision_curve)
        except:
            auc_roc = 0.0
            auc_pr = 0.0

        # Confusion matrix components
        tn, fp, fn, tp = confusion_matrix(labels, pred_labels).ravel()

        # Specificity and sensitivity
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0

        # False positive and false negative rates
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        return {
            # Overall metrics
            "accuracy": accuracy,
            "balanced_accuracy": balanced_acc,
            "f1_macro": f1_macro,
            "mcc": mcc,
            # AUC metrics
            "auc_roc": auc_roc,
            "auc_pr": auc_pr,
            # Per-class metrics
            "precision_benign": precision[0],
            "recall_benign": recall[0],
            "f1_benign": f1[0],
            "precision_pathogenic": precision[1],
            "recall_pathogenic": recall[1],
            "f1_pathogenic": f1[1],
            # Clinical metrics
            "sensitivity": sensitivity,
            "specificity": specificity,
            "fpr": fpr,
            "fnr": fnr,
        }

    # ========================================================================
    # STEP 5: TRAINING CONFIGURATION
    # ========================================================================

    output_dir = "/models/dna-classifier-improved"

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=WARMUP_STEPS,
        learning_rate=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=GRADIENT_CLIP,  # Gradient clipping
        # Logging and evaluation
        logging_dir="/models/logs",
        logging_steps=10,
        logging_strategy="steps",
        # Evaluation strategy for overfitting detection
        eval_strategy="steps",
        eval_steps=50,
        # Checkpointing
        save_strategy="steps",
        save_steps=50,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_f1_macro",  # Use F1 instead of loss
        greater_is_better=True,
        # Performance
        fp16=True,  # Mixed precision
        dataloader_num_workers=4,
        # Misc
        report_to="none",
        seed=SEED,
    )

    # Early stopping to prevent overfitting
    early_stopping = EarlyStoppingCallback(
        early_stopping_patience=5,  # Stop if no improvement for 5 evaluations
        early_stopping_threshold=0.001,  # Minimum improvement threshold
    )

    # ========================================================================
    # STEP 6: TRAIN MODEL
    # ========================================================================

    print("\n🚀 Initializing Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_comprehensive_metrics,
        callbacks=[early_stopping],
    )

    print("\n" + "=" * 80)
    print("🎯 Starting Training...")
    print("=" * 80)

    # Train!
    train_result = trainer.train()

    print("\n✅ Training Complete!")

    # ========================================================================
    # STEP 7: EVALUATION ON TEST SET
    # ========================================================================

    print("\n📊 Evaluating on Test Set...")
    test_results = trainer.evaluate(test_dataset)

    # Get detailed predictions
    predictions = trainer.predict(test_dataset)
    pred_probs = torch.softmax(torch.tensor(predictions.predictions), dim=1)[
        :, 1
    ].numpy()
    pred_labels = np.argmax(predictions.predictions, axis=1)
    true_labels = predictions.label_ids

    # ========================================================================
    # STEP 8: GENERATE COMPREHENSIVE EVALUATION PLOTS
    # ========================================================================

    print("\n📈 Generating Evaluation Plots...")

    plots_dir = "/models/plots"
    os.makedirs(plots_dir, exist_ok=True)

    plt.style.use("default")
    sns.set_palette("husl")

    # 1. Training History (Overfitting Detection)
    if hasattr(trainer.state, "log_history"):
        history = trainer.state.log_history

        train_loss = [x["loss"] for x in history if "loss" in x]
        eval_loss = [x["eval_loss"] for x in history if "eval_loss" in x]

        if train_loss and eval_loss:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

            # Loss curves
            steps_train = list(range(len(train_loss)))
            steps_eval = [
                i * (len(train_loss) // len(eval_loss)) for i in range(len(eval_loss))
            ]

            ax1.plot(steps_train, train_loss, label="Train Loss", linewidth=2)
            ax1.plot(steps_eval, eval_loss, label="Validation Loss", linewidth=2)
            ax1.set_xlabel("Step")
            ax1.set_ylabel("Loss")
            ax1.set_title("Training vs Validation Loss (Overfitting Detection)")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # F1 score over time
            eval_f1 = [
                x.get("eval_f1_macro", 0) for x in history if "eval_f1_macro" in x
            ]
            if eval_f1:
                ax2.plot(
                    steps_eval[: len(eval_f1)],
                    eval_f1,
                    label="Validation F1",
                    linewidth=2,
                    color="green",
                )
                ax2.set_xlabel("Step")
                ax2.set_ylabel("F1 Score")
                ax2.set_title("Validation F1 Score Over Time")
                ax2.legend()
                ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(
                f"{plots_dir}/training_history.png", dpi=300, bbox_inches="tight"
            )
            plt.close()

    # 2. Confusion Matrix
    cm = confusion_matrix(true_labels, pred_labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Benign", "Pathogenic"],
        yticklabels=["Benign", "Pathogenic"],
        cbar_kws={"label": "Count"},
    )
    plt.title("Confusion Matrix\n", fontsize=14, fontweight="bold")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")

    # Add percentages
    cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    for i in range(2):
        for j in range(2):
            plt.text(
                j + 0.5,
                i + 0.7,
                f"({cm_percent[i, j]:.1f}%)",
                ha="center",
                va="center",
                fontsize=10,
                color="gray",
            )

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3. ROC Curve
    fpr, tpr, _ = roc_curve(true_labels, pred_probs)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, linewidth=2, label=f"ROC Curve (AUC = {roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate (Recall)")
    plt.title("Receiver Operating Characteristic (ROC) Curve")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/roc_curve.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. Precision-Recall Curve (Better for imbalanced data)
    precision_curve, recall_curve, _ = precision_recall_curve(true_labels, pred_probs)
    pr_auc = auc(recall_curve, precision_curve)

    plt.figure(figsize=(8, 8))
    plt.plot(
        recall_curve,
        precision_curve,
        linewidth=2,
        label=f"PR Curve (AUC = {pr_auc:.3f})",
    )
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall (Sensitivity)")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve\n(More suitable for imbalanced data)")
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/precision_recall_curve.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 5. Metrics Comparison Bar Chart
    metrics_data = {
        "Metric": [
            "Accuracy",
            "Balanced\nAccuracy",
            "F1 (Macro)",
            "MCC",
            "AUC-ROC",
            "AUC-PR",
        ],
        "Score": [
            test_results["eval_accuracy"],
            test_results["eval_balanced_accuracy"],
            test_results["eval_f1_macro"],
            test_results["eval_mcc"],
            test_results["eval_auc_roc"],
            test_results["eval_auc_pr"],
        ],
    }

    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        metrics_data["Metric"],
        metrics_data["Score"],
        color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"],
    )
    plt.ylim([0, 1.0])
    plt.ylabel("Score")
    plt.title(
        "Comprehensive Evaluation Metrics\n(Multiple metrics to assess model fairly)",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/metrics_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 6. Per-Class Performance
    class_metrics = {
        "Class": ["Benign", "Pathogenic"],
        "Precision": [
            test_results["eval_precision_benign"],
            test_results["eval_precision_pathogenic"],
        ],
        "Recall": [
            test_results["eval_recall_benign"],
            test_results["eval_recall_pathogenic"],
        ],
        "F1-Score": [
            test_results["eval_f1_benign"],
            test_results["eval_f1_pathogenic"],
        ],
    }

    class_df = pd.DataFrame(class_metrics).set_index("Class")

    fig, ax = plt.subplots(figsize=(10, 6))
    class_df.plot(kind="bar", ax=ax, width=0.8)
    plt.ylim([0, 1.0])
    plt.ylabel("Score")
    plt.title(
        "Per-Class Performance Metrics\n(Both classes evaluated separately)",
        fontsize=14,
        fontweight="bold",
    )
    plt.xticks(rotation=0)
    plt.legend(title="Metric", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/per_class_metrics.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 7. Prediction Distribution
    plt.figure(figsize=(12, 6))

    benign_probs = pred_probs[true_labels == 0]
    pathogenic_probs = pred_probs[true_labels == 1]

    plt.hist(
        benign_probs,
        bins=30,
        alpha=0.7,
        label="True Benign",
        color="green",
        density=True,
    )
    plt.hist(
        pathogenic_probs,
        bins=30,
        alpha=0.7,
        label="True Pathogenic",
        color="red",
        density=True,
    )
    plt.axvline(
        x=0.5, color="black", linestyle="--", linewidth=2, label="Decision Threshold"
    )
    plt.xlabel("Predicted Probability (Pathogenic)")
    plt.ylabel("Density")
    plt.title(
        "Distribution of Predicted Probabilities by True Class",
        fontsize=14,
        fontweight="bold",
    )
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{plots_dir}/prediction_distribution.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    print(f"   ✅ Plots saved to: {plots_dir}")

    # ========================================================================
    # STEP 9: SAVE COMPREHENSIVE RESULTS
    # ========================================================================

    print("\n💾 Saving Results...")

    # Classification report
    class_report = classification_report(
        true_labels,
        pred_labels,
        target_names=["Benign", "Pathogenic"],
        output_dict=True,
    )

    # Compile comprehensive results
    results = {
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "model_type": "DNASequenceClassifier",
            "hidden_size": 768,
            "num_layers": 6,
            "num_epochs": NUM_EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "dropout": DROPOUT,
            "gradient_clip": GRADIENT_CLIP,
            "seed": SEED,
        },
        "dataset": {
            "train_samples": len(train_dataset),
            "val_samples": len(val_dataset),
            "test_samples": len(test_dataset),
            "pathogenic_count": int(pathogenic_train),
            "benign_count": int(benign_train),
            "imbalance_ratio": float(
                max(pathogenic_train, benign_train)
                / min(pathogenic_train, benign_train)
            ),
        },
        "class_weights": {
            "benign": float(class_weights[0]),
            "pathogenic": float(class_weights[1]),
        },
        "test_metrics": {
            # Primary metrics (for imbalanced data)
            "balanced_accuracy": float(test_results["eval_balanced_accuracy"]),
            "f1_macro": float(test_results["eval_f1_macro"]),
            "mcc": float(test_results["eval_mcc"]),
            "auc_pr": float(test_results["eval_auc_pr"]),
            # Additional metrics
            "accuracy": float(test_results["eval_accuracy"]),
            "auc_roc": float(test_results["eval_auc_roc"]),
            # Per-class metrics
            "benign": {
                "precision": float(test_results["eval_precision_benign"]),
                "recall": float(test_results["eval_recall_benign"]),
                "f1": float(test_results["eval_f1_benign"]),
            },
            "pathogenic": {
                "precision": float(test_results["eval_precision_pathogenic"]),
                "recall": float(test_results["eval_recall_pathogenic"]),
                "f1": float(test_results["eval_f1_pathogenic"]),
            },
            # Clinical metrics
            "sensitivity": float(test_results["eval_sensitivity"]),
            "specificity": float(test_results["eval_specificity"]),
            "false_positive_rate": float(test_results["eval_fpr"]),
            "false_negative_rate": float(test_results["eval_fnr"]),
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": class_report,
        "training_time_seconds": train_result.metrics.get("train_runtime", 0),
    }

    # Save results
    results_path = "/models/training_results_improved.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Save model
    final_model_path = "/models/dna-classifier-final"
    trainer.save_model(final_model_path)

    print(f"   ✅ Model saved to: {final_model_path}")
    print(f"   ✅ Results saved to: {results_path}")

    # ========================================================================
    # STEP 10: PRINT SUMMARY
    # ========================================================================

    print("\n" + "=" * 80)
    print("🎉 Training Complete!")
    print("=" * 80)

    print("\n📊 Test Set Performance:")
    print(f"   {'Metric':<30} {'Score':<10}")
    print(f"   {'-' * 40}")
    print(f"   {'Balanced Accuracy':<30} {test_results['eval_balanced_accuracy']:.4f}")
    print(f"   {'F1 Score (Macro)':<30} {test_results['eval_f1_macro']:.4f}")
    print(f"   {'Matthews Correlation Coef.':<30} {test_results['eval_mcc']:.4f}")
    print(f"   {'AUC-PR (for imbalanced data)':<30} {test_results['eval_auc_pr']:.4f}")
    print(f"   {'AUC-ROC':<30} {test_results['eval_auc_roc']:.4f}")
    print(f"   {'Accuracy':<30} {test_results['eval_accuracy']:.4f}")

    print(f"\n   {'Per-Class Performance:'}")
    print(f"   {'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print(f"   {'-' * 51}")
    print(
        f"   {'Benign':<15} {test_results['eval_precision_benign']:.4f}       "
        f"{test_results['eval_recall_benign']:.4f}       {test_results['eval_f1_benign']:.4f}"
    )
    print(
        f"   {'Pathogenic':<15} {test_results['eval_precision_pathogenic']:.4f}       "
        f"{test_results['eval_recall_pathogenic']:.4f}       {test_results['eval_f1_pathogenic']:.4f}"
    )

    print(f"\n   {'Clinical Metrics:'}")
    print(f"   {'Sensitivity (Recall)':<30} {test_results['eval_sensitivity']:.4f}")
    print(f"   {'Specificity':<30} {test_results['eval_specificity']:.4f}")
    print(f"   {'False Positive Rate':<30} {test_results['eval_fpr']:.4f}")
    print(f"   {'False Negative Rate':<30} {test_results['eval_fnr']:.4f}")

    print(f"\n✅ All evaluation plots saved to: {plots_dir}")
    print(f"✅ Comprehensive results saved to: {results_path}")

    return results


@app.local_entrypoint()
def main():
    """Local entrypoint to trigger training"""
    print("🚀 Launching Improved Training on Modal...")
    print("   This addresses defense feedback about:")
    print("   - Using appropriate metrics for imbalanced data")
    print("   - Implementing class weighting")
    print("   - Detecting overfitting/underfitting")
    print("   - Reporting per-class performance")
    print()

    result = train_with_comprehensive_metrics.remote()

    print("\n" + "=" * 80)
    if "error" in result:
        print(f"❌ Training failed: {result['error']}")
    else:
        print("✅ Training completed successfully!")
        print("\n📊 Key Results:")
        print(
            f"   Balanced Accuracy: {result['test_metrics']['balanced_accuracy']:.4f}"
        )
        print(f"   F1 Score (Macro): {result['test_metrics']['f1_macro']:.4f}")
        print(f"   MCC: {result['test_metrics']['mcc']:.4f}")
        print(f"   AUC-PR: {result['test_metrics']['auc_pr']:.4f}")

    return result


if __name__ == "__main__":
    main()
