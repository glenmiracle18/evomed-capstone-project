"""
Quick baseline model using Random Forest with engineered features
This addresses the underfitting problem by using meaningful features
"""

import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    auc,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

print("=" * 80)
print("EvoMed - Random Forest Baseline with Feature Engineering")
print("=" * 80)

# Load data
print("\n📂 Loading preprocessed data...")
train_df = pd.read_csv("data/processed/train.csv")
val_df = pd.read_csv("data/processed/val.csv")
test_df = pd.read_csv("data/processed/test.csv")

print(f"   Train: {len(train_df):,} variants")
print(f"   Val: {len(val_df):,} variants")
print(f"   Test: {len(test_df):,} variants")

# Feature Engineering
print("\n🔧 Engineering Features...")


def extract_features(df):
    """
    Extract meaningful features from variant data
    """
    features = pd.DataFrame()

    # Position features
    features["position"] = df["position"]
    features["position_normalized"] = (df["position"] - df["position"].min()) / (
        df["position"].max() - df["position"].min()
    )

    # Variant type features
    features["ref_length"] = df["ref"].astype(str).str.len()
    features["alt_length"] = df["alt"].astype(str).str.len()
    features["length_diff"] = features["alt_length"] - features["ref_length"]

    # Variant type classification
    features["is_snv"] = (features["ref_length"] == 1) & (features["alt_length"] == 1)
    features["is_insertion"] = features["alt_length"] > features["ref_length"]
    features["is_deletion"] = features["alt_length"] < features["ref_length"]

    # African frequency features
    features["af_afr"] = df["af_afr"].fillna(0)
    features["has_afr_data"] = (df["af_afr"] > 0).astype(int)
    features["log_af_afr"] = np.log10(df["af_afr"].fillna(1e-6) + 1e-6)

    # Frequency categories
    features["afr_rare"] = (df["af_afr"] < 0.001).astype(int)
    features["afr_uncommon"] = ((df["af_afr"] >= 0.001) & (df["af_afr"] < 0.01)).astype(
        int
    )
    features["afr_common"] = (df["af_afr"] >= 0.01).astype(int)

    # Sequence features (simple)
    features["ref_gc_content"] = (
        df["ref"]
        .astype(str)
        .apply(lambda x: (x.count("G") + x.count("C")) / max(len(x), 1))
    )
    features["alt_gc_content"] = (
        df["alt"]
        .astype(str)
        .apply(lambda x: (x.count("G") + x.count("C")) / max(len(x), 1))
    )

    return features


X_train = extract_features(train_df)
X_val = extract_features(val_df)
X_test = extract_features(test_df)

y_train = train_df["label"].values
y_val = val_df["label"].values
y_test = test_df["label"].values

print(f"   ✅ Extracted {X_train.shape[1]} features per variant")
print(f"   Feature names: {list(X_train.columns)}")

# Train Random Forest
print("\n🌳 Training Random Forest...")

# Use balanced class weights
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced",  # Automatically handles imbalance
    random_state=42,
    n_jobs=-1,
    verbose=1,
)

model.fit(X_train, y_train)
print("   ✅ Training complete!")

# Predictions
print("\n📊 Evaluating model...")
y_pred_train = model.predict(X_train)
y_pred_val = model.predict(X_val)
y_pred_test = model.predict(X_test)

y_pred_proba_train = model.predict_proba(X_train)[:, 1]
y_pred_proba_val = model.predict_proba(X_val)[:, 1]
y_pred_proba_test = model.predict_proba(X_test)[:, 1]


# Comprehensive metrics
def compute_all_metrics(y_true, y_pred, y_pred_proba):
    """Compute all metrics"""
    metrics = {}

    # Basic
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["balanced_accuracy"] = balanced_accuracy_score(y_true, y_pred)
    metrics["f1_macro"] = f1_score(y_true, y_pred, average="macro")
    metrics["mcc"] = matthews_corrcoef(y_true, y_pred)

    # AUC
    try:
        metrics["auc_roc"] = roc_auc_score(y_true, y_pred_proba)
        precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_pred_proba)
        metrics["auc_pr"] = auc(recall_curve, precision_curve)
    except:
        metrics["auc_roc"] = 0.0
        metrics["auc_pr"] = 0.0

    # Per-class
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()

        # Benign (0)
        metrics["precision_benign"] = tn / (tn + fn) if (tn + fn) > 0 else 0
        metrics["recall_benign"] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics["f1_benign"] = (
            2
            * metrics["precision_benign"]
            * metrics["recall_benign"]
            / (metrics["precision_benign"] + metrics["recall_benign"])
            if (metrics["precision_benign"] + metrics["recall_benign"]) > 0
            else 0
        )

        # Pathogenic (1)
        metrics["precision_pathogenic"] = tp / (tp + fp) if (tp + fp) > 0 else 0
        metrics["recall_pathogenic"] = tp / (tp + fn) if (tp + fn) > 0 else 0
        metrics["f1_pathogenic"] = (
            2
            * metrics["precision_pathogenic"]
            * metrics["recall_pathogenic"]
            / (metrics["precision_pathogenic"] + metrics["recall_pathogenic"])
            if (metrics["precision_pathogenic"] + metrics["recall_pathogenic"]) > 0
            else 0
        )

        # Clinical
        metrics["sensitivity"] = tp / (tp + fn) if (tp + fn) > 0 else 0
        metrics["specificity"] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics["fpr"] = fp / (fp + tn) if (fp + tn) > 0 else 0
        metrics["fnr"] = fn / (fn + tp) if (fn + tp) > 0 else 0

    return metrics


train_metrics = compute_all_metrics(y_train, y_pred_train, y_pred_proba_train)
val_metrics = compute_all_metrics(y_val, y_pred_val, y_pred_proba_val)
test_metrics = compute_all_metrics(y_test, y_pred_test, y_pred_proba_test)

print(f"\n   Train Metrics:")
print(f"      Balanced Accuracy: {train_metrics['balanced_accuracy']:.4f}")
print(f"      F1 (Macro): {train_metrics['f1_macro']:.4f}")
print(f"      MCC: {train_metrics['mcc']:.4f}")

print(f"\n   Validation Metrics:")
print(f"      Balanced Accuracy: {val_metrics['balanced_accuracy']:.4f}")
print(f"      F1 (Macro): {val_metrics['f1_macro']:.4f}")
print(f"      MCC: {val_metrics['mcc']:.4f}")

print(f"\n   Test Metrics:")
print(f"      Balanced Accuracy: {test_metrics['balanced_accuracy']:.4f}")
print(f"      F1 (Macro): {test_metrics['f1_macro']:.4f}")
print(f"      MCC: {test_metrics['mcc']:.4f}")

# Feature importance
print("\n🔍 Feature Importance:")
feature_importance = pd.DataFrame(
    {"feature": X_train.columns, "importance": model.feature_importances_}
).sort_values("importance", ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']:30} {row['importance']:.4f}")

# Generate plots
print("\n📈 Generating plots...")
os.makedirs("results/plots", exist_ok=True)

# 1. Confusion Matrix
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_pred_test)
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Benign", "Pathogenic"],
    yticklabels=["Benign", "Pathogenic"],
)
plt.title("Confusion Matrix - Random Forest")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
plt.savefig("results/plots/rf_confusion_matrix.png", dpi=300)
plt.close()

# 2. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba_test)
plt.figure(figsize=(8, 8))
plt.plot(fpr, tpr, linewidth=2, label=f"ROC (AUC = {test_metrics['auc_roc']:.3f})")
plt.plot([0, 1], [0, 1], "k--", linewidth=1)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Random Forest")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/plots/rf_roc_curve.png", dpi=300)
plt.close()

# 3. Feature Importance
plt.figure(figsize=(10, 8))
feature_importance.head(15).plot(x="feature", y="importance", kind="barh", legend=False)
plt.xlabel("Importance")
plt.title("Top 15 Most Important Features")
plt.tight_layout()
plt.savefig("results/plots/rf_feature_importance.png", dpi=300)
plt.close()

# 4. Training vs Validation Metrics
metrics_comparison = pd.DataFrame(
    {
        "Metric": ["Balanced\nAccuracy", "F1 (Macro)", "MCC", "AUC-ROC", "AUC-PR"],
        "Train": [
            train_metrics["balanced_accuracy"],
            train_metrics["f1_macro"],
            train_metrics["mcc"],
            train_metrics["auc_roc"],
            train_metrics["auc_pr"],
        ],
        "Validation": [
            val_metrics["balanced_accuracy"],
            val_metrics["f1_macro"],
            val_metrics["mcc"],
            val_metrics["auc_roc"],
            val_metrics["auc_pr"],
        ],
        "Test": [
            test_metrics["balanced_accuracy"],
            test_metrics["f1_macro"],
            test_metrics["mcc"],
            test_metrics["auc_roc"],
            test_metrics["auc_pr"],
        ],
    }
)

plt.figure(figsize=(12, 6))
x = np.arange(len(metrics_comparison))
width = 0.25
plt.bar(x - width, metrics_comparison["Train"], width, label="Train", alpha=0.8)
plt.bar(x, metrics_comparison["Validation"], width, label="Validation", alpha=0.8)
plt.bar(x + width, metrics_comparison["Test"], width, label="Test", alpha=0.8)
plt.xlabel("Metric")
plt.ylabel("Score")
plt.title("Model Performance Across Splits")
plt.xticks(x, metrics_comparison["Metric"])
plt.legend()
plt.ylim(0, 1.0)
plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig("results/plots/rf_metrics_comparison.png", dpi=300)
plt.close()

print("   ✅ Plots saved to results/plots/")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "model_type": "RandomForestClassifier",
    "configuration": {
        "n_estimators": 200,
        "max_depth": 10,
        "class_weight": "balanced",
        "random_state": 42,
    },
    "dataset": {
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "features": list(X_train.columns),
        "n_features": len(X_train.columns),
    },
    "metrics": {
        "train": {k: float(v) for k, v in train_metrics.items()},
        "validation": {k: float(v) for k, v in val_metrics.items()},
        "test": {k: float(v) for k, v in test_metrics.items()},
    },
    "feature_importance": feature_importance.to_dict("records"),
    "confusion_matrix": cm.tolist(),
}

os.makedirs("results", exist_ok=True)
with open("results/random_forest_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n💾 Results saved to results/random_forest_results.json")

# Print summary
print("\n" + "=" * 80)
print("🎉 Random Forest Training Complete!")
print("=" * 80)

print("\n📊 Test Set Performance:")
print(f"   Balanced Accuracy:     {test_metrics['balanced_accuracy']:.4f}")
print(f"   F1 Score (Macro):      {test_metrics['f1_macro']:.4f}")
print(f"   MCC:                   {test_metrics['mcc']:.4f}")
print(f"   AUC-ROC:               {test_metrics['auc_roc']:.4f}")
print(f"   AUC-PR:                {test_metrics['auc_pr']:.4f}")

print(f"\n   Per-Class Performance:")
print(f"   {'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
print(f"   {'-' * 51}")
print(
    f"   {'Benign':<15} {test_metrics['precision_benign']:.4f}       {test_metrics['recall_benign']:.4f}       {test_metrics['f1_benign']:.4f}"
)
print(
    f"   {'Pathogenic':<15} {test_metrics['precision_pathogenic']:.4f}       {test_metrics['recall_pathogenic']:.4f}       {test_metrics['f1_pathogenic']:.4f}"
)

# Check for overfitting
print(f"\n   Overfitting Check:")
print(f"   Train F1:              {train_metrics['f1_macro']:.4f}")
print(f"   Validation F1:         {val_metrics['f1_macro']:.4f}")
print(f"   Test F1:               {test_metrics['f1_macro']:.4f}")
diff = abs(train_metrics["f1_macro"] - test_metrics["f1_macro"])
if diff < 0.05:
    print(f"   ✅ Good generalization (diff: {diff:.4f})")
elif diff < 0.10:
    print(f"   ⚠️  Slight overfitting (diff: {diff:.4f})")
else:
    print(f"   🔴 Overfitting detected (diff: {diff:.4f})")

print(f"\n✅ All results and plots saved!")
print(f"   JSON: results/random_forest_results.json")
print(f"   Plots: results/plots/rf_*.png")
