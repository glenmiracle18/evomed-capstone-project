import numpy as np
import pandas as pd
import pytest
from scripts.prepare_training_data import (
    parse_clinical_significance,
    process_brca_exchange_dataset,
    split_dataset,
)


@pytest.mark.parametrize(
    "sig_str, expected",
    [
        ("Pathogenic", 1),
        ("Likely pathogenic", 1),
        ("Benign", 0),
        ("Likely benign", 0),
        ("Uncertain significance", -1),
        ("Conflicting interpretations of pathogenicity", -1),
        (np.nan, -1),
    ],
)
def test_parse_clinical_significance(sig_str, expected):
    """Test parsing of clinical significance strings"""
    assert parse_clinical_significance(sig_str) == expected


def test_process_brca_exchange_dataset():
    """Test processing of the BRCA Exchange dataset"""
    # Create a sample dataframe
    raw_data = {
        "Clinical_Significance_ENIGMA": [
            "Pathogenic",
            "Benign",
            "Uncertain significance",
        ],
        "Genomic_Coordinate_hg38": [
            "chr17:43044295:G>A",
            "chr17:43044296:C>T",
            "chr17:43044297:A>G",
        ],
        "Allele_Frequency_AFR": ["0.001", "0.01", "."],
        "Ref": ["G", "C", "A"],
        "Alt": ["A", "T", "G"],
    }
    df = pd.DataFrame(raw_data)

    # Process the dataframe
    processed_df = process_brca_exchange_dataset(df)

    # Assertions
    assert len(processed_df) == 2  # Uncertain significance should be removed
    assert "label" in processed_df.columns
    assert processed_df["label"].tolist() == [1, 0]
    assert "af_afr" in processed_df.columns
    assert pd.api.types.is_numeric_dtype(processed_df["af_afr"])


def test_split_dataset():
    """Test the dataset splitting logic"""
    # Create a sample dataframe
    data = {"label": np.random.randint(0, 2, 100)}
    df = pd.DataFrame(data)

    # Split the dataset
    splits = split_dataset(df)

    # Assertions
    assert "train" in splits
    assert "val" in splits
    assert "test" in splits
    assert len(splits["train"]) + len(splits["val"]) + len(splits["test"]) == 100

    # Check for no overlap
    train_indices = splits["train"].index
    val_indices = splits["val"].index
    test_indices = splits["test"].index
    assert len(train_indices.intersection(val_indices)) == 0
    assert len(train_indices.intersection(test_indices)) == 0
    assert len(val_indices.intersection(test_indices)) == 0
