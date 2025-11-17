from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from services.brca_exchange_api import BRCAExchangeAPI


@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get"""
    with patch("requests.get") as mock_get:
        yield mock_get


def test_fetch_variants_success(mock_requests_get):
    """Test successful API call"""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "Gene_Symbol": "BRCA1",
            "Genomic_Coordinate_hg38": "chr17:43044295:G>A",
            "Clinical_Significance_ENIGMA": "Pathogenic",
            "Allele_Frequency_AFR": "0.001",
        }
    ]
    mock_requests_get.return_value = mock_response

    # Call the method
    api = BRCAExchangeAPI()
    df = api.fetch_variants(gene_symbol="BRCA1")

    # Assertions
    assert not df.empty
    assert len(df) == 1
    assert "Gene_Symbol" in df.columns
    assert df.iloc[0]["Gene_Symbol"] == "BRCA1"


def test_fetch_variants_api_error(mock_requests_get):
    """Test API returning an error"""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_requests_get.return_value = mock_response

    # Call the method
    api = BRCAExchangeAPI()
    df = api.fetch_variants(gene_symbol="BRCA1")

    # Assertions
    assert df.empty


def test_fetch_variants_empty_response(mock_requests_get):
    """Test API returning an empty list"""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_requests_get.return_value = mock_response

    # Call the method
    api = BRCAExchangeAPI()
    df = api.fetch_variants(gene_symbol="BRCA1")

    # Assertions
    assert df.empty
