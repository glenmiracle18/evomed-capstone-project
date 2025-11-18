"""
Debug script to test different gnomAD API query formats
"""
import requests
import json

def test_gnomad_query_formats():
    """Try different query formats to find what works"""

    base_url = "https://gnomad.broadinstitute.org/api"

    # Test 1: Try to get available datasets
    print("=" * 70)
    print("TEST 1: Query available datasets")
    print("=" * 70)

    query1 = """
    {
      meta {
        datasets
      }
    }
    """

    try:
        response = requests.post(
            base_url,
            json={"query": query1},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Try simple variant query with different dataset names
    print("\n" + "=" * 70)
    print("TEST 2: Try variant query with gnomad_r4")
    print("=" * 70)

    variant_id = "1-55516888-G-A"  # Common variant for testing

    query2 = """
    query VariantQuery($variantId: String!, $datasetId: DatasetId!) {
      variant(variantId: $variantId, dataset: $datasetId) {
        variant_id
        pos
      }
    }
    """

    for dataset in ["gnomad_r4", "gnomad_r3", "gnomAD_r4", "gnomad_v4"]:
        print(f"\nTrying dataset: {dataset}")
        try:
            response = requests.post(
                base_url,
                json={
                    "query": query2,
                    "variables": {
                        "variantId": variant_id,
                        "datasetId": dataset
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"  Errors: {data['errors'][0].get('message', '')[:100]}")
                else:
                    print(f"  ✅ SUCCESS!")
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}")
                    break
            else:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Test 3: Try without dataset parameter
    print("\n" + "=" * 70)
    print("TEST 3: Try variant query without dataset parameter")
    print("=" * 70)

    query3 = """
    query {
      variant(variant_id: "1-55516888-G-A") {
        variant_id
        pos
      }
    }
    """

    try:
        response = requests.post(
            base_url,
            json={"query": query3},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:300]}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Try gnomAD browser web API instead
    print("\n" + "=" * 70)
    print("TEST 4: Try gnomAD REST API alternative")
    print("=" * 70)

    rest_url = "https://gnomad.broadinstitute.org/api/variant/1-55516888-G-A"
    try:
        response = requests.get(rest_url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ REST API works!")
            print(f"Response preview: {response.text[:200]}")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gnomad_query_formats()
