"""
Modal training script for Random Forest with Feature Engineering
This is a cloud version of the successful local Random Forest approach
"""

import modal

# Modal app definition
app = modal.App("evomed-rf-training")

# Create Modal image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "joblib>=1.3.0",
)

# Create Modal volumes for data persistence
data_volume = modal.Volume.from_name("evomed-training-data", create_if_missing=True)
results_volume = modal.Volume.from_name("evomed-rf-results", create_if_missing=True)


@app.function(
    image=image,
    timeout=600,  # 10 minutes (should only take ~2 seconds though)
    volumes={
        "/data": data_volume,
        "/results": results_volume,
    },
)
def train_random_forest():
    """
    Train Random Forest with engineered features for BRCA1 variant classification
    """
    import json
    import os
    from datetime import datetime

    import joblib
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
        precision_recall_fscore_support,
        roc_auc_score,
        roc_curve,
    )

    print("=" * 80)
    print("EvoMed - Random Forest Baseline with Feature Engineering")
    print("=" * 80)

    # Reload volumes to ensure data is accessible
    print("\n📂 Reloading data volume...")
    data_volume.reload()

    # Debug: List files in /data directory
    import os

    print("\n🔍 Checking /data directory contents:")
    if os.path.exists("/data"):
        files = os.listdir("/data")
        print(f"   Files found: {files}")
        for f in files:
            full_path = os.path.join("/data", f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                print(f"   - {f} ({size:,} bytes)")
    else:
        print("   ❌ /data directory does not exist!")

    # Load preprocessed data
    print("\n📂 Loading preprocessed data...")
    train_df = pd.read_csv("/data/data/train.csv")
    val_df = pd.read_csv("/data/data/val.csv")
    test_df = pd.read_csv("/data/data/test.csv")

    print(f"   Train: {len(train_df):,} variants")
    print(f"   Val: {len(val_df):,} variants")
    print(f"   Test: {len(test_df):,} variants")

    # Feature engineering function
    def extract_features(df):
        """Extract meaningful features from variant data"""
        features = pd.DataFrame()

        # Position features
        features["position"] = df["position"]
        features["position_normalized"] = (df["position"] - df["position"].min()) / (
            df["position"].max() - df["position"].min()
        )

        # Sequence length features
        ref_length = df["ref"].str.len()
        alt_length = df["alt"].str.len()
        features["ref_length"] = ref_length
        features["alt_length"] = alt_length
        features["length_diff"] = alt_length - ref_length

        # Variant type features
        features["is_snv"] = ((ref_length == 1) & (alt_length == 1)).astype(int)
        features["is_insertion"] = (alt_length > ref_length).astype(int)
        features["is_deletion"] = (alt_length < ref_length).astype(int)

        # African frequency features
        features["af_afr"] = df["af_afr"].fillna(0)
        features["has_afr_data"] = (df["af_afr"] > 0).astype(int)
        features["log_af_afr"] = np.log10(df["af_afr"] + 1e-10)

        # Frequency categories
        features["afr_rare"] = (df["af_afr"] < 0.001).astype(int)
        features["afr_uncommon"] = (
            (df["af_afr"] >= 0.001) & (df["af_afr"] < 0.01)
        ).astype(int)
        features["afr_common"] = (df["af_afr"] >= 0.01).astype(int)

        # GC content
        def calc_gc_content(seq):
            if pd.isna(seq) or len(seq) == 0:
                return 0.5
            seq = str(seq).upper()
            gc_count = seq.count("G") + seq.count("C")
            return gc_count / len(seq) if len(seq) > 0 else 0.5

        features["ref_gc_content"] = df["ref"].apply(calc_gc_content)
        features["alt_gc_content"] = df["alt"].apply(calc_gc_content)

        return features

    print("\n🔧 Engineering Features...")
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
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",  # Handles class imbalance
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )

    model.fit(X_train, y_train)
    print("   ✅ Training complete!")

    # Evaluate on all splits
    def evaluate_split(X, y, split_name):
        """Evaluate model on a data split"""
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)[:, 1]

        # Calculate comprehensive metrics
        metrics = {
            "balanced_accuracy": balanced_accuracy_score(y, y_pred),
            "f1_macro": f1_score(y, y_pred, average="macro"),
            "mcc": matthews_corrcoef(y, y_pred),
            "auc_roc": roc_auc_score(y, y_pred_proba),
        }

        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y, y_pred, average=None
        )
        metrics["benign_precision"] = precision[0]
        metrics["benign_recall"] = recall[0]
        metrics["benign_f1"] = f1[0]
        metrics["pathogenic_precision"] = precision[1]
        metrics["pathogenic_recall"] = recall[1]
        metrics["pathogenic_f1"] = f1[1]

        # Precision-Recall AUC
        prec_curve, rec_curve, _ = precision_recall_curve(y, y_pred_proba)
        metrics["auc_pr"] = auc(rec_curve, prec_curve)

        return metrics, y_pred, y_pred_proba

    print("\n📊 Evaluating model...")
    train_metrics, _, _ = evaluate_split(X_train, y_train, "Train")
    val_metrics, _, _ = evaluate_split(X_val, y_val, "Validation")
    test_metrics, y_test_pred, y_test_proba = evaluate_split(X_test, y_test, "Test")

    # Print metrics
    for split_name, metrics in [
        ("Train", train_metrics),
        ("Validation", val_metrics),
        ("Test", test_metrics),
    ]:
        print(f"\n   {split_name} Metrics:")
        print(f"      Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
        print(f"      F1 (Macro): {metrics['f1_macro']:.4f}")
        print(f"      MCC: {metrics['mcc']:.4f}")

    # Feature importance
    print("\n🔍 Feature Importance:")
    feature_importance = pd.DataFrame(
        {"feature": X_train.columns, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)

    for _, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']:<30} {row['importance']:.4f}")

    # Generate plots
    print("\n📈 Generating plots...")
    plots_dir = "/results/plots"
    os.makedirs(plots_dir, exist_ok=True)

    # Set style
    plt.style.use("default")
    sns.set_palette("husl")

    # 1. Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(8, 6))
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
    # Add performance metrics text
    plt.text(
        0.5,
        -0.15,
        f"Balanced Acc: {test_metrics['balanced_accuracy']:.3f} | F1 (Macro): {test_metrics['f1_macro']:.3f} | MCC: {test_metrics['mcc']:.3f}",
        ha="center",
        transform=plt.gca().transAxes,
        fontsize=10,
    )
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/rf_confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_test_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, linewidth=2, label=f"AUC = {test_metrics['auc_roc']:.3f}")
    plt.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Random Forest")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/rf_roc_curve.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3. Feature Importance
    plt.figure(figsize=(10, 8))
    top_features = feature_importance.head(15)
    plt.barh(range(len(top_features)), top_features["importance"])
    plt.yticks(range(len(top_features)), top_features["feature"])
    plt.xlabel("Importance")
    plt.title("Top 15 Feature Importances")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/rf_feature_importance.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. Metrics Comparison (Train vs Val vs Test)
    metrics_comparison = pd.DataFrame(
        {
            "Train": [
                train_metrics["balanced_accuracy"],
                train_metrics["f1_macro"],
                train_metrics["mcc"],
                train_metrics["auc_roc"],
            ],
            "Validation": [
                val_metrics["balanced_accuracy"],
                val_metrics["f1_macro"],
                val_metrics["mcc"],
                val_metrics["auc_roc"],
            ],
            "Test": [
                test_metrics["balanced_accuracy"],
                test_metrics["f1_macro"],
                test_metrics["mcc"],
                test_metrics["auc_roc"],
            ],
        },
        index=["Balanced Accuracy", "F1 (Macro)", "MCC", "AUC-ROC"],
    )

    plt.figure(figsize=(10, 6))
    metrics_comparison.plot(kind="bar", ax=plt.gca())
    plt.title("Model Performance Across Splits")
    plt.ylabel("Score")
    plt.xlabel("Metric")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Split")
    plt.ylim([0, 1.0])
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/rf_metrics_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"   ✅ Plots saved to: {plots_dir}")

    # Save model
    print("\n💾 Saving model...")
    model_path = "/results/random_forest_model.joblib"
    joblib.dump(model, model_path)
    print(f"   ✅ Model saved to: {model_path}")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "model_type": "RandomForestClassifier",
        "model_config": {
            "n_estimators": 200,
            "max_depth": 10,
            "class_weight": "balanced",
        },
        "data_splits": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df),
        },
        "features": {
            "count": len(X_train.columns),
            "names": list(X_train.columns),
        },
        "metrics": {
            "train": {k: float(v) for k, v in train_metrics.items()},
            "validation": {k: float(v) for k, v in val_metrics.items()},
            "test": {k: float(v) for k, v in test_metrics.items()},
        },
        "feature_importance": {
            row["feature"]: float(row["importance"])
            for _, row in feature_importance.iterrows()
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(
            y_test, y_test_pred, target_names=["Benign", "Pathogenic"], output_dict=True
        ),
    }

    results_path = "/results/random_forest_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to {results_path}")

    # Print final summary
    print("\n" + "=" * 80)
    print("🎉 Random Forest Training Complete!")
    print("=" * 80)

    print(f"\n📊 Test Set Performance:")
    print(f"   Balanced Accuracy:     {test_metrics['balanced_accuracy']:.4f}")
    print(f"   F1 Score (Macro):      {test_metrics['f1_macro']:.4f}")
    print(f"   MCC:                   {test_metrics['mcc']:.4f}")
    print(f"   AUC-ROC:               {test_metrics['auc_roc']:.4f}")
    print(f"   AUC-PR:                {test_metrics['auc_pr']:.4f}")

    print(f"\n   Per-Class Performance:")
    print(f"   Class           Precision    Recall       F1-Score")
    print(f"   ---------------------------------------------------")
    print(
        f"   Benign          {test_metrics['benign_precision']:.4f}       {test_metrics['benign_recall']:.4f}       {test_metrics['benign_f1']:.4f}"
    )
    print(
        f"   Pathogenic      {test_metrics['pathogenic_precision']:.4f}       {test_metrics['pathogenic_recall']:.4f}       {test_metrics['pathogenic_f1']:.4f}"
    )

    print(f"\n   Overfitting Check:")
    print(f"   Train F1:              {train_metrics['f1_macro']:.4f}")
    print(f"   Validation F1:         {val_metrics['f1_macro']:.4f}")
    print(f"   Test F1:               {test_metrics['f1_macro']:.4f}")
    train_test_diff = abs(train_metrics["f1_macro"] - test_metrics["f1_macro"])
    if train_test_diff < 0.05:
        print(f"   ✅ Good generalization (diff: {train_test_diff:.4f})")
    else:
        print(f"   ⚠️  Possible overfitting (diff: {train_test_diff:.4f})")

    print(f"\n✅ All results and plots saved!")
    print(f"   JSON: {results_path}")
    print(f"   Model: {model_path}")
    print(f"   Plots: {plots_dir}/rf_*.png")

    # Commit volumes to persist data
    results_volume.commit()

    return results


@app.local_entrypoint()
def main():
    """Local entrypoint to trigger training"""
    print("🚀 Launching Random Forest training on Modal...")
    print("   Using CPU (no GPU needed for Random Forest)")
    print()

    result = train_random_forest.remote()

    print("\n" + "=" * 80)
    print("✅ Training completed successfully!")
    print("\n📊 Key Results:")
    print(f"   Balanced Accuracy: {result['metrics']['test']['balanced_accuracy']:.4f}")
    print(f"   F1 Score (Macro):  {result['metrics']['test']['f1_macro']:.4f}")
    print(f"   MCC:               {result['metrics']['test']['mcc']:.4f}")
    print(f"   AUC-ROC:           {result['metrics']['test']['auc_roc']:.4f}")

    print(
        "\n💡 To download results: modal volume get evomed-rf-results /results/random_forest_results.json ."
    )
    print(
        "💡 To download plots: modal volume get evomed-rf-results /results/plots/ . -r"
    )

    return result


if __name__ == "__main__":
    main()
