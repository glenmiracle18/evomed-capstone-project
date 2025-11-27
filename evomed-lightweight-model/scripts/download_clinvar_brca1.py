"""
Download BRCA1 variants from ClinVar directly - more reliable than BRCA Exchange API
"""

import pandas as pd
import requests
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from configs.config import DATA_DIR

def download_clinvar_brca1():
    """Download BRCA1 variants directly from ClinVar API"""
    
    print("🔬 Downloading BRCA1 variants from ClinVar API...")
    
    # ClinVar eSearch API to get BRCA1 variant IDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "clinvar",
        "term": "BRCA1[gene] AND single_gene[properties]",
        "retmax": "10000",
        "retmode": "json"
    }
    
    print("   Searching for BRCA1 variants...")
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    
    variant_ids = search_data["esearchresult"]["idlist"]
    print(f"   Found {len(variant_ids)} BRCA1 variant IDs")
    
    if not variant_ids:
        print("   ❌ No BRCA1 variants found")
        return False
    
    # Get detailed variant information
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    # Process in batches of 200 (API limit)
    batch_size = 200
    all_variants = []
    
    for i in range(0, len(variant_ids), batch_size):
        batch_ids = variant_ids[i:i+batch_size]
        print(f"   Processing batch {i//batch_size + 1}/{(len(variant_ids)-1)//batch_size + 1}...")
        
        fetch_params = {
            "db": "clinvar",
            "id": ",".join(batch_ids),
            "retmode": "json"
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params)
        batch_data = fetch_response.json()
        
        # Extract variant information
        for variant_id, variant_info in batch_data["result"].items():
            if variant_id == "uids":
                continue
                
            try:
                # Extract key information
                variant = {
                    "id": variant_id,
                    "title": variant_info.get("title", ""),
                    "clinical_significance": variant_info.get("clinical_significance", ""),
                    "variation_type": variant_info.get("variation_type", ""),
                    "chromosome": variant_info.get("chromosome", ""),
                    "gene_symbol": "BRCA1",
                    "review_status": variant_info.get("review_status", ""),
                    "last_evaluated": variant_info.get("last_evaluated", ""),
                    "germline_classification": variant_info.get("germline_classification", ""),
                }
                
                # Parse genomic coordinates from title if available
                title = variant_info.get("title", "")
                if "NM_007294" in title or "c." in title:
                    variant["hgvs_c"] = title
                    
                all_variants.append(variant)
                
            except Exception as e:
                print(f"     Warning: Error processing variant {variant_id}: {e}")
                continue
    
    # Convert to DataFrame
    df = pd.DataFrame(all_variants)
    print(f"   ✅ Processed {len(df)} BRCA1 variants")
    
    # Filter for pathogenic/benign variants
    pathogenic_terms = ["pathogenic", "likely pathogenic"]
    benign_terms = ["benign", "likely benign"]
    
    df["label"] = -1  # Unknown
    df.loc[df["clinical_significance"].str.lower().str.contains("|".join(pathogenic_terms), na=False), "label"] = 1
    df.loc[df["clinical_significance"].str.lower().str.contains("|".join(benign_terms), na=False), "label"] = 0
    
    labeled_df = df[df["label"] != -1]
    print(f"   Pathogenic/Likely Pathogenic: {len(labeled_df[labeled_df['label'] == 1])}")
    print(f"   Benign/Likely Benign: {len(labeled_df[labeled_df['label'] == 0])}")
    print(f"   Total labeled variants: {len(labeled_df)}")
    
    # Save the data
    output_path = DATA_DIR / "clinvar_brca1.csv"
    labeled_df.to_csv(output_path, index=False)
    print(f"   💾 Saved to: {output_path}")
    
    return True

if __name__ == "__main__":
    success = download_clinvar_brca1()
    if success:
        print("\n🎉 ClinVar BRCA1 data downloaded successfully!")
    else:
        print("\n❌ Failed to download ClinVar data")