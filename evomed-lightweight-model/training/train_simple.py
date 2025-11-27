"""
Simple, self-contained BERT training for variant classification
Avoids all DNABERT-2 and flash attention issues
"""

import sys
from pathlib import Path

import modal

# Modal app definition
app = modal.App("simple-variant-training")

# Simple image with just the essentials
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch>=2.0.0",
    "transformers>=4.35.0",
    "datasets>=2.14.0",
    "accelerate>=0.24.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
)

# Modal volumes
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)
model_volume = modal.Volume.from_name("evomed-trained-models", create_if_missing=True)

@app.function(
    image=image,
    gpu="A100",
    timeout=7200,
    volumes={
        "/data": data_volume,
        "/models": model_volume,
    },
)
def train_simple_variant_classifier():
    """Train a simple variant classifier without DNABERT-2 complications"""
    
    import json
    import os
    from datetime import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import torch
    import torch.nn as nn
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        precision_recall_curve,
        precision_recall_fscore_support,
        roc_auc_score,
        roc_curve,
    )
    from sklearn.model_selection import train_test_split
    from transformers import AutoTokenizer, AutoModel

    print("=" * 70)
    print("Simple Variant Classification Training")
    print("=" * 70)

    # Load and process dataset
    print("\nLoading and processing dataset...")
    df = pd.read_csv("/data/variants(1).tsv", sep='\t', low_memory=False)
    print(f"Loaded {len(df):,} total variants")

    # Process clinical significance
    def parse_clinical_significance(row):
        """Parse clinical significance to binary label"""
        # Check ENIGMA first
        enigma_sig = str(row.get('Clinical_significance_ENIGMA', '')).lower()
        if 'pathogenic' in enigma_sig and 'benign' not in enigma_sig:
            return 1
        elif 'benign' in enigma_sig and 'pathogenic' not in enigma_sig:
            return 0
        
        # Check ClinVar
        clinvar_sig = str(row.get('Clinical_Significance_ClinVar', '')).lower()
        if 'pathogenic' in clinvar_sig and 'benign' not in clinvar_sig:
            return 1
        elif 'benign' in clinvar_sig and 'pathogenic' not in clinvar_sig:
            return 0
        
        return -1  # Unknown

    df['label'] = df.apply(parse_clinical_significance, axis=1)
    df_filtered = df[df['label'] != -1].copy()
    print(f"Filtered to {len(df_filtered):,} variants with known pathogenicity")

    # Extract African frequency
    def get_african_frequency(row):
        afr_cols = ['Allele_frequency_AFR_GnomAD', 
                   'Allele_frequency_genome_AFR_GnomAD',
                   'Allele_frequency_exome_AFR_GnomAD']
        
        for col in afr_cols:
            if col in row and pd.notna(row[col]) and row[col] != '-':
                try:
                    return float(row[col])
                except:
                    continue
        return 0.0

    df_filtered['af_afr'] = df_filtered.apply(get_african_frequency, axis=1)

    # Apply African adjustment
    def apply_african_adjustment(row):
        base_label = row['label']
        af_afr = row['af_afr']
        
        if af_afr > 0.05:  # High frequency in AFR
            if base_label == 1:  # Predicted pathogenic
                return 0  # Adjust to benign
        return base_label

    df_filtered['adjusted_label'] = df_filtered.apply(apply_african_adjustment, axis=1)

    # Create simple sequence features instead of tokenizing
    def create_simple_features(row):
        """Create simple numeric features from variant data"""
        ref = str(row.get('Ref', 'N'))
        alt = str(row.get('Alt', 'N'))
        pos = row.get('Pos', 0)
        
        # Simple features based on variant characteristics
        features = [
            len(ref),  # Reference length
            len(alt),  # Alternative length
            abs(len(alt) - len(ref)),  # Length difference
            hash(ref) % 1000,  # Reference hash
            hash(alt) % 1000,  # Alternative hash
            pos % 10000,  # Position modulo
            row['af_afr'] if pd.notna(row['af_afr']) else 0,  # AFR frequency
        ]
        
        # Pad to fixed length
        while len(features) < 20:
            features.append(0)
        
        return features[:20]  # Fixed 20 features

    print("\nCreating simple features...")
    feature_data = []
    labels = []
    
    for _, row in df_filtered.iterrows():
        try:
            features = create_simple_features(row)
            feature_data.append(features)
            labels.append(int(row['adjusted_label']))
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    # Convert to numpy arrays
    X = np.array(feature_data, dtype=np.float32)
    y = np.array(labels, dtype=np.int64)

    print(f"Created feature matrix: {X.shape}")
    print(f"Labels shape: {y.shape}")

    # Train test split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.67, random_state=42, stratify=y_temp
    )

    print(f"Train: {X_train.shape[0]} samples")
    print(f"Val: {X_val.shape[0]} samples") 
    print(f"Test: {X_test.shape[0]} samples")

    # Simple neural network model
    class SimpleClassifier(nn.Module):
        def __init__(self, input_dim=20, num_labels=2):
            super().__init__()
            self.classifier = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(64, num_labels)
            )
            
        def forward(self, x):
            return self.classifier(x)

    # Training setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    
    model = SimpleClassifier().to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training loop
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train).to(device)
    y_train_tensor = torch.LongTensor(y_train).to(device)
    X_val_tensor = torch.FloatTensor(X_val).to(device)
    y_val_tensor = torch.LongTensor(y_val).to(device)
    X_test_tensor = torch.FloatTensor(X_test).to(device)
    y_test_tensor = torch.LongTensor(y_test).to(device)

    print("\nStarting training...")
    batch_size = 64
    epochs = 50
    
    best_val_acc = 0
    train_losses = []
    val_accs = []
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        # Mini-batch training
        for i in range(0, len(X_train_tensor), batch_size):
            batch_X = X_train_tensor[i:i+batch_size]
            batch_y = y_train_tensor[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_preds = torch.argmax(val_outputs, dim=1)
            val_acc = accuracy_score(y_val_tensor.cpu(), val_preds.cpu())
            
        train_losses.append(total_loss / (len(X_train_tensor) // batch_size))
        val_accs.append(val_acc)
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "/models/best_model.pth")
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Loss={total_loss:.4f}, Val Acc={val_acc:.4f}")

    # Load best model for evaluation
    model.load_state_dict(torch.load("/models/best_model.pth"))
    model.eval()

    # Test evaluation
    print("\nEvaluating on test set...")
    with torch.no_grad():
        test_outputs = model(X_test_tensor)
        test_probs = torch.softmax(test_outputs, dim=1)[:, 1].cpu().numpy()
        test_preds = torch.argmax(test_outputs, dim=1).cpu().numpy()
        test_labels = y_test_tensor.cpu().numpy()

    # Calculate metrics
    test_acc = accuracy_score(test_labels, test_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_labels, test_preds, average='binary'
    )
    
    try:
        auc = roc_auc_score(test_labels, test_probs)
    except:
        auc = 0.0

    print(f"\nTest Results:")
    print(f"Accuracy: {test_acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1: {f1:.4f}")
    print(f"AUC: {auc:.4f}")

    # Generate plots
    print("\nGenerating evaluation plots...")
    plots_dir = "/models/plots"
    os.makedirs(plots_dir, exist_ok=True)

    plt.style.use('default')
    
    # 1. Training curves
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(val_accs)
    plt.title('Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/training_curves.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Confusion Matrix
    cm = confusion_matrix(test_labels, test_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Benign', 'Pathogenic'],
                yticklabels=['Benign', 'Pathogenic'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 3. ROC Curve
    if auc > 0:
        fpr, tpr, _ = roc_curve(test_labels, test_probs)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', linewidth=1)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/roc_curve.png", dpi=300, bbox_inches='tight')
        plt.close()

    # 4. African Frequency Analysis
    adjustments_made = (df_filtered['label'] != df_filtered['adjusted_label']).sum()
    
    plt.figure(figsize=(10, 6))
    benign_af = df_filtered[df_filtered['adjusted_label'] == 0]['af_afr']
    pathogenic_af = df_filtered[df_filtered['adjusted_label'] == 1]['af_afr']
    
    plt.hist(benign_af[benign_af > 0], bins=30, alpha=0.7, label='Benign', density=True)
    plt.hist(pathogenic_af[pathogenic_af > 0], bins=30, alpha=0.7, label='Pathogenic', density=True)
    plt.xlabel('African Allele Frequency')
    plt.ylabel('Density')
    plt.title(f'African Frequency Distribution (Adjustments: {adjustments_made})')
    plt.legend()
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/african_frequency_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "model_type": "Simple Neural Network",
        "total_variants": len(df),
        "processed_variants": len(df_filtered),
        "african_adjustments": int(adjustments_made),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "test_results": {
            "accuracy": float(test_acc),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "auc": float(auc)
        },
        "best_val_accuracy": float(best_val_acc)
    }

    with open("/models/training_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nTraining complete!")
    print(f"African adjustments made: {adjustments_made}")
    print(f"Plots saved to: {plots_dir}")
    print(f"Results saved to: /models/training_results.json")

    return results

@app.local_entrypoint()
def main():
    """Local entrypoint to trigger training"""
    print("Launching simple variant classifier training...")
    result = train_simple_variant_classifier.remote()
    
    print("\nTraining completed!")
    print(f"Final results: {result}")
    return result

if __name__ == "__main__":
    main()